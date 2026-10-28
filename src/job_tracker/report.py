import statistics
from datetime import date


def status_breakdown(conn):
    result = conn.execute("""
        SELECT application_status, COUNT(*)
        FROM applications
        GROUP BY application_status
    """).fetchall()
    return result

def lane_response_rate(conn):
    result = conn.execute("""
        SELECT fit_lane, COUNT(*) AS total_applications,
            SUM(CASE WHEN application_status != 'application_received' THEN 1 Else 0 END) AS moved_past_received
        FROM applications
        GROUP BY fit_lane
    """).fetchall()
    return result

def employer_type_response_rate(conn):
    result = conn.execute("""
        SELECT employer_type, COUNT(*) AS total_applications,
            SUM(CASE WHEN application_status != 'application_received' THEN 1 Else 0 END) AS moved_past_received
        FROM applications
        GROUP BY employer_type
    """).fetchall()
    return result

def salary_distribution_by_lane(conn, column="salary_min"):
    result = conn.execute(f"""
        SELECT fit_lane, MIN({column}) AS min_salary, AVG({column}) AS avg_salary, MAX({column}) AS max_salary
        FROM applications
        GROUP BY fit_lane
    """).fetchall()
    return result

def aging_applications(conn, days=30):
    result = conn.execute("""
        SELECT a.company, a.job_title, a.application_status,
            COALESCE(h.last_change, a.date_submitted) AS last_change,
            CAST(julianday(date('now')) - julianday(COALESCE(h.last_change, a.date_submitted)) AS INTEGER) AS days_aged
        FROM applications a
        LEFT JOIN (
            SELECT application_id, MAX(observed_on) AS last_change
            FROM status_history
            GROUP BY application_id
        ) h ON h.application_id = a.id
        WHERE a.application_status NOT IN ('rejected', 'no_longer_considered')
            AND days_aged >= ?
        ORDER BY days_aged DESC
    """, (days,)).fetchall()
    return result

def median_days(conn):
    # median query calculates median days from submission to first status change 
    result = conn.execute("""
        SELECT a.company, a.job_title, a.application_status,
            CAST(julianday(h.first_change) - julianday(a.date_submitted) AS INTEGER) AS days_to_first_change
        FROM applications a
        JOIN (
            SELECT application_id, MIN(observed_on) AS first_change -- Min keeps this correct once an app has multiple history rows
            FROM status_history
            GROUP BY application_id
        ) h ON h.application_id = a.id
    """).fetchall()

    days = [row[3] for row in result if row[3] is not None]
    median = statistics.median(days) if days else None # SQLite does not have a built-in median function, so we calculate it in Python

    return median, len(days)

# Write the report
def gather_results(conn):
    status_rows = status_breakdown(conn)
    lane_rows = lane_response_rate(conn)
    employer_rows = employer_type_response_rate(conn)
    salary_rows = salary_distribution_by_lane(conn)
    aging_rows = aging_applications(conn)

    median, count = median_days(conn)
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
    path.write_text(text.rstrip("\n") + "\n", encoding="utf-8")