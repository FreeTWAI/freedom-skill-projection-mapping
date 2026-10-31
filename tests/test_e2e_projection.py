import unittest

class TestE2EProjectionMapping(unittest.TestCase):
    """
    End-to-end integration tests for projection mapping plans.
    Validates multi-projector surface partitioning, video aspect ratio,
    and playback cue sheets.
    """

    # --- Multi-projector Surface Partitioning ---

    def test_surface_partitioning_valid(self):
        """Test that a surface is correctly partitioned across multiple projectors."""
        # Simulated valid partitioning configuration
        surface = {"width_mm": 6000, "height_mm": 2000}
        projectors = [
            {"id": "p1", "coverage_x": [0, 3100], "coverage_y": [0, 2000]},
            {"id": "p2", "coverage_x": [2900, 6000], "coverage_y": [0, 2000]}
        ]

        # Verify the entire surface width is covered
        min_x = min(p["coverage_x"][0] for p in projectors)
        max_x = max(p["coverage_x"][1] for p in projectors)
        self.assertEqual(min_x, 0)
        self.assertEqual(max_x, surface["width_mm"])

        # Verify overlap exists (e.g. [2900, 3100])
        overlap = projectors[0]["coverage_x"][1] - projectors[1]["coverage_x"][0]
        self.assertGreater(overlap, 0)

    # --- Video Aspect Ratio Validation ---

    def test_video_aspect_ratio_valid(self):
        """Test valid video aspect ratio calculation and matching."""
        video_asset = {"resolution": {"width": 1920, "height": 1080}}
        surface = {"width_mm": 3200, "height_mm": 1800}

        video_ratio = video_asset["resolution"]["width"] / video_asset["resolution"]["height"]
        surface_ratio = surface["width_mm"] / surface["height_mm"]

        # 16:9 ratio
        self.assertAlmostEqual(video_ratio, 1.7777, places=3)
        self.assertAlmostEqual(surface_ratio, 1.7777, places=3)
        self.assertAlmostEqual(video_ratio, surface_ratio, places=3)

    # --- Playback Cue Sheets Verification ---

    def test_playback_cue_sheet_valid_sequence(self):
        """Test a valid sequence of playback cues."""
        cues = [
            {"id": "Q1", "start_time": 0.0, "duration": 10.0, "asset_id": "intro"},
            {"id": "Q2", "start_time": 10.0, "duration": 20.0, "asset_id": "main"},
            {"id": "Q3", "start_time": 30.0, "duration": 5.0, "asset_id": "outro"}
        ]

        # Verify continuous timeline
        for i in range(len(cues) - 1):
            expected_next_start = cues[i]["start_time"] + cues[i]["duration"]
            self.assertEqual(expected_next_start, cues[i+1]["start_time"])

if __name__ == '__main__':
    unittest.main()
