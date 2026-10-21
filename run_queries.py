
from datetime import date

from extract import (
    DB_PATH,
    aging_applications,
    employer_type_response_rate,
    lane_response_rate,
    median_days,
    salary_distribution_by_lane,
    status_breakdown,
)

REPORT_PATH = BASE_DIR / "reports" / "report.md"

def calc_rate(responded, total):
    return round((responded / total) * 100, 1) if total > 0 else None

def rate_rows(rows):
    """returns a list of dictionaries with name, total, responses and rate"""
    return [
        {
            "name": category,
            "total": total,
            "responded": responded,
            "rate": calc_rate(responded, total),
        }
        for category, total, responded in rows
    ]

def gather_results(db_path):
    status_rows = status_breakdown(db_path)
    lane_rows = lane_response_rate(db_path)
    employer_rows = employer_type_response_rate(db_path)
    salary_rows = salary_distribution_by_lane(db_path)
    aging_rows = aging_applications(db_path)

    median, count = median_days(db_path)
    median_rows = {"median": median, "count": count}

    # Calculate total applications from status breakdown
    
    total_applications = sum(num_apps for _, num_apps in status_rows)

   
    # create named fields for lane_response_rate
    lane_rates = rate_rows(lane_rows)

    employer_rates = rate_rows(employer_rows)

    return {
        "total_applications": total_applications,
        "status_breakdown": dict(status_rows),
        "lane_response_rate": lane_rates,
        "employer_type_response_rate": employer_rates,
        "salary_distribution_by_lane": salary_rows,
        "aging_applications": aging_rows,
        "median_days": median_rows
    }

STATUS_ORDER = ["application_received", "in_review", "sme_review", "rejected", "no_longer_considered"]

def render_funnel_table(status_counts, total):
    lines = ["## Funnel Table", "", 
             "| Status | Count | Share |", "|---|---|---|"]
    ordered = STATUS_ORDER + [s for s in status_counts if s not in STATUS_ORDER]
    counted = 0
    for status in ordered:
        n = status_counts.get(status, 0)
        lines.append(f"| {status.replace('_', ' ')} | {n} | {calc_rate(n, total)}% |")
        counted += n
    lines.append(f"| **Total** | {counted} | {calc_rate(counted, total)}% |")
    return "\n".join(lines)

def render_rate_table(heading, label, rows):
    lines = [f"## {heading}", "",
             f"| {label} | Applications | Moved past received | Rate |",
             "| --- | --- | --- | --- |"]
    for row in rows:
        rate = "-" if row["rate"] is None else f"{row['rate']}%"
        lines.append(f"| {row['name']} | {row['total']} | {row['responded']} | {rate} |")
    return "\n".join(lines)


def render_report(results):
    today = date.today().isoformat()

    total_apps = results["total_applications"]

    received_count = results["status_breakdown"].get("application_received", 0)
    total_responded = total_apps - received_count
    overall_rate = calc_rate(total_responded, total_apps)

    med_info = results["median_days"]
    median_val = med_info["median"]
    median_n = med_info["count"]

    if median_val is not None:
        median_str = f"{median_val} days (n={median_n})"
    else:
        median_str = f"N/A (n={median_n})"

    report = "\n".join([
        "# JOB SEARCH PIPELINE REPORT",
        "",
        f"Generated on: {today}",
        "",
        f"- **Total applications** {total_apps}",
        f"- **Moved past received** {total_responded} ({overall_rate}%)",
        f"- **Median to first change:** {median_str}",
        "",
        render_funnel_table(results['status_breakdown'], total_apps),
        "",
        render_rate_table("Lane Response Rate", "Lane", results['lane_response_rate']),
        "",
        render_rate_table("Employer Type Response Rate", "Employer Type", results['employer_type_response_rate'])
        ]
    )

    return report

def write_report(text, path):
    path.parent.mkdir(parents=True, exist_ok=True)   # make the folder
    path.write_text(text.rstrip("\n") + "\n", encoding="utf-8")          # write (or overwrite) the file

if __name__ == "__main__":
    report_text = render_report(gather_results(DB_PATH))
    write_report(report_text, REPORT_PATH)
    print(f"Report written to {REPORT_PATH}")