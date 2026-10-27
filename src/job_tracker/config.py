from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

TRACKER_PATH = BASE_DIR / "data" / "tracker.xlsx"
EMPLOYER_TYPES_PATH = BASE_DIR / "employer_types.json"
EMPLOYER_TYPES_EXAMPLE_PATH = BASE_DIR / "employer_types_example.json"
DB_PATH = BASE_DIR / "tracker.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"
REPORT_PATH = BASE_DIR / "reports" / "report.md"