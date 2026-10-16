from extract import (
    BASE_DIR,
    aging_applications,
    employer_type_response_rate,
    lane_response_rate,
    median_days,
    salary_distribution_by_lane,
    status_breakdown,
)

DB_PATH = BASE_DIR / "tracker.db"

if __name__ == "__main__":
    print("Status Breakdown: \n", status_breakdown(DB_PATH))
    print("Lane Response Rate: \n", lane_response_rate(DB_PATH))
    print("Employer Type Response Rate: \n", employer_type_response_rate(DB_PATH))
    print("Salary Distribution by Lane: \n", salary_distribution_by_lane(DB_PATH))
    print("Aging Applications: \n", aging_applications(DB_PATH))
    median, count = median_days(DB_PATH)
    print("Median \n", f"Median Days: {median}, Count: {count}")
