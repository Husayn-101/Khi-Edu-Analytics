import json
import sqlite3
import tempfile
import sys
from pathlib import Path
import unittest

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from helpers import (  # noqa: E402
    get_public_analysis_columns,
    get_sensitive_columns,
    prepare_public_survey_data,
    validate_public_survey_data,
)

from pipeline import extract_transform_load, refresh_if_source_changed  # noqa: E402


class HelperPrivacyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.frame = pd.DataFrame(
            {
                "Age": [15, 16],
                "Gender": ["F", "M"],
                "Grade/Class": ["10", "11"],
                "Timestamp": ["2024-01-01", "2024-01-02"],
                "Student Number": [101, 102],
                "Preferred Study Method": ["Reading", "Group work"],
            }
        )

    def test_sensitive_columns_are_detected(self) -> None:
        sensitive_columns = get_sensitive_columns(self.frame)
        self.assertIn("Timestamp", sensitive_columns)
        self.assertIn("Student Number", sensitive_columns)

    def test_public_columns_keep_only_allowed_fields(self) -> None:
        public_columns = get_public_analysis_columns(self.frame)
        self.assertEqual(public_columns, ["Age", "Grade/Class", "Gender", "Preferred Study Method"])

    def test_public_export_drops_sensitive_columns(self) -> None:
        public_frame = prepare_public_survey_data(self.frame)
        self.assertNotIn("timestamp", public_frame.columns)
        self.assertNotIn("student_number", public_frame.columns)
        self.assertIn("age", public_frame.columns)

    def test_validate_public_data_raises_on_sensitive_fields(self) -> None:
        with self.assertRaises(ValueError):
            validate_public_survey_data(self.frame)


class PipelineETLTests(unittest.TestCase):
    def test_etl_refreshes_warehouse_and_public_export(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            source_path = temp_dir / "survey.csv"
            warehouse_dir = temp_dir / "warehouse"
            state_dir = temp_dir / "state"

            source_frame = pd.DataFrame(
                {
                    "Age": [15, 16],
                    "Gender": ["F", "M"],
                    "Grade/Class": ["10", "11"],
                    "Timestamp": ["2024-01-01", "2024-01-02"],
                    "Student Number": [101, 102],
                    "Preferred Study Method": ["Reading", "Group work"],
                }
            )
            source_frame.to_csv(source_path, index=False)

            state = extract_transform_load(
                source_filename="survey.csv",
                data_dir=temp_dir,
                warehouse_dir=warehouse_dir,
                state_dir=state_dir,
            )

            self.assertEqual(state["rows_loaded"], 2)
            self.assertTrue(Path(state["public_export_path"]).exists())
            self.assertTrue(Path(state["warehouse_path"]).exists())

            connection = sqlite3.connect(state["warehouse_path"])
            try:
                row_count = connection.execute("SELECT COUNT(*) FROM survey_clean").fetchone()[0]
            finally:
                connection.close()
            self.assertEqual(row_count, 2)

            state_file = state_dir / "pipeline_state.json"
            self.assertTrue(state_file.exists())
            saved_state = json.loads(state_file.read_text(encoding="utf-8"))
            self.assertEqual(saved_state["rows_loaded"], 2)

            no_change = refresh_if_source_changed(
                source_filename="survey.csv",
                data_dir=temp_dir,
                warehouse_dir=warehouse_dir,
                state_dir=state_dir,
            )
            self.assertIsNone(no_change)

            source_frame.loc[2] = [17, "F", "12", "2024-01-03", 103, "Self-study"]
            source_frame.to_csv(source_path, index=False)

            refreshed = refresh_if_source_changed(
                source_filename="survey.csv",
                data_dir=temp_dir,
                warehouse_dir=warehouse_dir,
                state_dir=state_dir,
            )
            self.assertIsNotNone(refreshed)
            self.assertEqual(refreshed["rows_loaded"], 3)


if __name__ == "__main__":
    unittest.main()