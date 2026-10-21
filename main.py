import argparse

def main():
    parser = argparse.ArgumentParser(prog="main")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="load tracker spreadhseet into the database")
    run.add_argument("--query", default="loading tracker into database")

    report = sub.add_parser("report", help="load data into report.md")
    report.add_argument("--rep", default="creating report from database")

    args = parser.parse_args()
    if args.command == "run":
        print(args.query)
    elif args.command == "report":
        print(args.rep)

if __name__ == "__main__":
    main()