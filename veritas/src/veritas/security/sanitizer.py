"""Air-Gap Observation Sanitizer for untrusted tool outputs.

Prevents indirect prompt injection attacks, delimiter injection, and memory poisoning
from untrusted external data (web pages, emails, Slack messages, third-party APIs).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


INDIRECT_INJECTION_PATTERNS = (
    re.compile(r"<\s*script\b[^>]*>(.*?)<\s*/\s*script\s*>", re.IGNORECASE | re.DOTALL),
    re.compile(r"ignore\s+(?:all\s+)?(?:previous|prior|above)\s+instructions?", re.IGNORECASE),
    re.compile(r"disregard\s+(?:all\s+)?(?:previous|prior)\s+commands?", re.IGNORECASE),
    re.compile(r"system\s+prompt\s+override", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+(?:a|an)\s+(?:developer|unrestricted|evil|admin)", re.IGNORECASE),
    re.compile(r"exfiltrate\s+(?:all\s+)?(?:keys?|passwords?|tokens?|secrets?)", re.IGNORECASE),
    re.compile(r"curl\s+https?://[^\s]+\s+-(?:d|-data)\s+[^\s]+", re.IGNORECASE),
    re.compile(r"\[SYSTEM(?:\s+MESSAGE)?\]", re.IGNORECASE),
    re.compile(r"<\s*\|\s*im_start\s*\|\s*>", re.IGNORECASE),
    re.compile(r"<\s*\|\s*im_end\s*\|\s*>", re.IGNORECASE),
)


@dataclass(frozen=True)
class SanitizedObservation:
    original_content: str
    clean_content: str
    is_tainted: bool
    detected_threats: tuple[str, ...]
    sanitizer_action: str  # 'pass', 'defanged', 'quarantined'


@dataclass(frozen=True)
class AirGapSanitizer:
    """Low-latency air-gap sanitizer acting as the Sentinel Model boundary."""

    quarantine_on_critical: bool = True
    defang_markdown_injections: bool = True

    def sanitize(self, raw_observation: str, *, source_name: str = "untrusted_tool") -> SanitizedObservation:
        threats: list[str] = []
        clean = raw_observation

        for pattern in INDIRECT_INJECTION_PATTERNS:
            matches = pattern.findall(clean)
            if matches:
                threats.append(f"Indirect injection pattern: {pattern.pattern}")
                if self.defang_markdown_injections:
                    # Defang pattern by wrapping it in sanitized quote block
                    clean = pattern.sub(r"[DEFANGED_INJECTION_ATTEMPT]", clean)

        if threats:
            action = "quarantined" if self.quarantine_on_critical and len(threats) > 1 else "defanged"
            return SanitizedObservation(
                original_content=raw_observation,
                clean_content=clean if action == "defanged" else "[OBSERVATION_QUARANTINED_DUE_TO_SECURITY_VIOLATION]",
                is_tainted=True,
                detected_threats=tuple(threats),
                sanitizer_action=action,
            )

        return SanitizedObservation(
            original_content=raw_observation,
            clean_content=raw_observation,
            is_tainted=False,
            detected_threats=(),
            sanitizer_action="pass",
        )
