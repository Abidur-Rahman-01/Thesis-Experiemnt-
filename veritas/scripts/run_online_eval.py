"""Run the local online demo."""

from __future__ import annotations

import sys

from veritas.__main__ import main


if __name__ == "__main__":
    if "--demo" not in sys.argv:
        sys.argv.append("--demo")
    main()
