import argparse
import logging
import sqlite3
from pathlib import Path

from . import config, extract, load, report, validate

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    parser = argparse.ArgumentParser(prog="main")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="load tracker spreadsheet into the database")
    run.add_argument(
        "--file",
        type=Path,
        default=config.TRACKER_PATH,
        help="path to tracker file (default: %(default)s)",
    )
    run.add_argument(
        "--schema",
        type=Path,
        default=config.SCHEMA_PATH,
        help="path to sql schema (default: %(default)s)",
    )
    run.add_argument(
        "--db",
        type=Path,
        default=config.DB_PATH,
        help="path to the SQLite database (default: %(default)s)",
    )

    report_parser = sub.add_parser("report", help="write data into report.md")
    report_parser.add_argument(
        "--output",
        type=Path,
        default=config.REPORT_PATH,
        help="where to write the report (default: %(default)s)",
    )
    report_parser.add_argument(
        "--db",
        type=Path,
        default=config.DB_PATH,
        help="path to the SQLite database (default: %(default)s)",
    )

    args = parser.parse_args()
    if args.command == "run":
        if not args.file.exists():
            parser.error(f"tracker not found: {args.file}")
        df = extract.load_tracker(args.file)
        validate.validate_tracker(df)
        # 1 open connection
        conn = sqlite3.connect(args.db)
        # 2 handle DB Creation
        load.create_database(conn, args.schema)
        # 3 pass the connection object
        before = load.get_all_stored_statuses(conn)
        load.insert_applications(df, conn)
        load.sync_statuses(df, before, conn)
        # 4 close the connection
        conn.close()
        logger.info("Loaded %d applications into %s", len(df), args.db)
    elif args.command == "report":
        if not args.db.exists():
            parser.error(f"database not found: {args.db}")
        # open connection
        conn = sqlite3.connect(args.db)
        # route through report namespace
        text = report.render_report(report.gather_results(conn))
        report.write_report(text, args.output)
        # close connection
        conn.close()
        logger.info("Report written to %s", args.output)


if __name__ == "__main__":
    main()
