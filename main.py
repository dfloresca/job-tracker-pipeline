import argparse
from pathlib import Path

from run_queries import (
    DB_PATH,
    REPORT_PATH,
    gather_results,
    render_report,
    write_report,
)


def main():
    parser = argparse.ArgumentParser(prog="main")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="load tracker spreadsheet into the database")
    run.add_argument("--db", type=Path, default="loading tracker into database")

    report = sub.add_parser("report", help="load data into report.md")
    report.add_argument("--output", type=Path, default=REPORT_PATH,
                    help="where to write the report (default: %(default)s)")
    report.add_argument("--db", type=Path, default=DB_PATH,
                    help="path to the SQLite database (default: %(default)s)")

    args = parser.parse_args()
    if args.command == "report":
        if not args.db.exists():
            parser.error(f"database not found: {args.db}")
        text = render_report(gather_results(args.db))
        write_report(text, args.output)
        print(f"Report written to {args.output}")
    elif args.command == "run":
        print("run: not wired yet")

if __name__ == "__main__":
    main()