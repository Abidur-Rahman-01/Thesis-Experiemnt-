import unittest

from veritas.risk.calibrator import TemperatureCalibrator, brier_score


class CalibratorTests(unittest.TestCase):
    def test_temperature_calibrator_outputs_probability(self) -> None:
        calibrator = TemperatureCalibrator(temperature=2.0)

        probability = calibrator.calibrate(1.0)

        self.assertGreater(probability, 0.0)
        self.assertLess(probability, 1.0)

    def test_fit_returns_usable_temperature(self) -> None:
        raw = [-3.0, -2.0, 2.0, 3.0]
        labels = [0, 0, 1, 1]
        calibrator = TemperatureCalibrator.fit(raw, labels)
        probs = calibrator.calibrate_many(raw)

        self.assertGreater(calibrator.temperature, 0)
        self.assertLess(brier_score(probs, labels), 0.1)
