import unittest
import time
from scripts.validate import validate

class TestPerformanceBenchmark(unittest.TestCase):
    def test_validation_performance_large_payload(self):
        """Benchmark validation with a large number of surfaces, assets, and cues."""
        num_items = 20000
        surfaces = [{"id": f"s{i}", "width_mm": 1000, "height_mm": 1000} for i in range(num_items)]
        assets = [{"id": f"a{i}", "source": "src", "rights": "rt", "duration_seconds": 10.0} for i in range(num_items)]
        cues = [{"id": f"c{i}", "surface_id": f"s{i}", "asset_id": f"a{i}", "duration_seconds": 5.0, "operator_role": "op", "fallback": "fb"} for i in range(num_items)]

        data = {
            "title": "Perf Test",
            "data_classification": "synthetic",
            "kind": "projection-mapping",
            "surfaces": surfaces,
            "assets": assets,
            "cues": cues
        }

        start_time = time.time()
        errors = validate(data)
        duration = time.time() - start_time

        self.assertEqual(errors, [])
        # Expect performance to be well under 1 second for 20000 items
        self.assertLess(duration, 1.0, f"Validation took too long: {duration:.3f} seconds")

if __name__ == '__main__':
    unittest.main()
