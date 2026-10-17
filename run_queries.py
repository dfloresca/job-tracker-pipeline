from pprint import pprint

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

    def calc_rate(responded, total):
        return round((responded / total) * 100, 1) if total > 0 else 0
    
    # create named fields for lane_response_rate
    lane_rates = [
        {"lane": lane,
         "total": total,
         "responded": responded,
         "rate": calc_rate(responded, total)}  
        for lane, total, responded in lane_rows
    ]

    return {
        "total_applications": total_applications,
        "lane_response_rate": lane_rates,
        "employer_type_response_rate": employer_rows,
        "salary_distribution_by_lane": salary_rows,
        "aging_applications": aging_rows,
        "median_days": median_rows
    }


if __name__ == "__main__":
    print("Run 3")
    pprint(gather_results(DB_PATH))