import argparse
import logging
from pathlib import Path

from run_queries import (
    gather_results,
    render_report,
    write_report,
)
from src.job_tracker.config import DB_PATH, REPORT_PATH, SCHEMA_PATH, TRACKER_PATH
from src.job_tracker.extract import (
    create_database,
    get_all_stored_statuses,
    insert_applications,
    load_tracker,
    sync_statuses,
)
from src.job_tracker.validate import validate_tracker

logger = logging.getLogger(__name__)

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(prog="main")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="load tracker spreadsheet into the database")
    run.add_argument("--file", type=Path, default=TRACKER_PATH,
                     help="path to tracker file (default: %(default)s)")
    run.add_argument("--schema", type=Path, default=SCHEMA_PATH,
                     help="path to sql schema (default: %(default)s)")
    run.add_argument("--db", type=Path, default=DB_PATH,
                    help="path to the SQLite database (default: %(default)s)")

    report = sub.add_parser("report", help="write data into report.md")
    report.add_argument("--output", type=Path, default=REPORT_PATH,
                    help="where to write the report (default: %(default)s)")
    report.add_argument("--db", type=Path, default=DB_PATH,
                    help="path to the SQLite database (default: %(default)s)")

    args = parser.parse_args()
    if args.command == "run":
        if not args.file.exists():
            parser.error(f"tracker not found: {args.file}")
        df = load_tracker(args.file)
        validate_tracker(df)
        create_database(args.db, args.schema)
        before = get_all_stored_statuses(args.db)
        insert_applications(df, args.db)
        sync_statuses(df, before, args.db)
        logger.info("Loaded %d applications into %s", len(df), args.db)
    elif args.command == "report":
        if not args.db.exists():
            parser.error(f"database not found: {args.db}")
        text = render_report(gather_results(args.db))
        write_report(text, args.output)
        logger.info("Report written to %s", args.output)
    
if __name__ == "__main__":
    main()