from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

TRACKER_PATH = BASE_DIR / "data" / "Washington_Job_tracker_v2_9_19_1.xlsx"
DB_PATH = BASE_DIR / "tracker.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"
REPORT_PATH = BASE_DIR / "reports" / "report.md"