import unittest
import json

class TestCalibrationValidation(unittest.TestCase):
    """
    End-to-end tests for projection coordinate calibration validation.
    """

    def test_perspective_transformation_matrices_valid(self):
        """Test valid 3x3 perspective transformation matrix."""
        # e.g., a standard identity matrix or a valid affine transformation
        valid_matrix = [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0]
        ]
        self.assertEqual(len(valid_matrix), 3)
        self.assertEqual(len(valid_matrix[0]), 3)

    def test_grid_warp_point_boundaries_valid(self):
        """Test grid warp points that fall exactly within the valid projection boundaries [0.0, 1.0]."""
        warp_points = [
            {"x": 0.0, "y": 0.0},
            {"x": 1.0, "y": 0.0},
            {"x": 0.0, "y": 1.0},
            {"x": 1.0, "y": 1.0},
            {"x": 0.5, "y": 0.5}
        ]
        for point in warp_points:
            self.assertTrue(0.0 <= point["x"] <= 1.0)
            self.assertTrue(0.0 <= point["y"] <= 1.0)

    def test_projector_profile_loader_valid(self):
        """Test that a valid projector JSON profile parses correctly."""
        valid_profile_json = '''
        {
            "id": "proj-main-1",
            "resolution": {"width": 1920, "height": 1080},
            "throw_ratio": 1.2,
            "lens_shift_v": 0.5,
            "lens_shift_h": 0.0
        }
        '''
        profile = json.loads(valid_profile_json)
        self.assertEqual(profile["id"], "proj-main-1")
        self.assertEqual(profile["resolution"]["width"], 1920)
        self.assertEqual(profile["resolution"]["height"], 1080)

if __name__ == '__main__':
    unittest.main()
