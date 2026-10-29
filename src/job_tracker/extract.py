import json
import logging

import pandas as pd

from src.job_tracker.config import (
    EMPLOYER_TYPES_EXAMPLE_PATH,
    EMPLOYER_TYPES_PATH,
)

from .transform import (
    classify_close_date,
    classify_employer,
    normalize_status,
    parse_salary,
)

logger = logging.getLogger(__name__)


def load_employer_rules(
    real_path=EMPLOYER_TYPES_PATH, example_path=EMPLOYER_TYPES_EXAMPLE_PATH
):
    path = real_path if real_path.exists() else example_path
    logger.info("Employer rules: %s", path)
    with path.open(encoding="utf-8") as f:
        rules = json.load(f)
    return rules


def load_tracker(path):
    df_active = pd.read_excel(path, sheet_name="Active Applications").assign(
        source_sheet="Active Applications"
    )
    df_archived = pd.read_excel(path, sheet_name="Archived Applications").assign(
        source_sheet="Archived Applications"
    )
    df_combined = pd.concat([df_active, df_archived], ignore_index=True)
    df_combined.columns = (
        df_combined.columns.astype(str)
        .str.replace(r"[^\w\s]", " ", regex=True)
        .str.strip()
        .str.replace(r"\s+", "_", regex=True)
        .str.lower()
    )
    df_combined["application_status"] = normalize_status(
        df_combined["application_status"]
    )
    df_combined["close_date_status"] = classify_close_date(
        df_combined["posting_close_date"]
    )
    df_combined["posting_close_date"] = pd.to_datetime(
        df_combined["posting_close_date"], errors="coerce"
    )
    df_combined["date_submitted"] = pd.to_datetime(
        df_combined["date_submitted"], errors="coerce"
    )
    # compute days_since_submitted as the difference between now and date_submitted normalizeing times for consistency
    df_combined["days_since_submitted"] = (
        pd.Timestamp.now().normalize() - df_combined["date_submitted"]
    ).dt.days
    # parse the salary range into min, max, and pay basis columns
    df_combined[["salary_min", "salary_max", "salary_pay_basis"]] = (
        df_combined["posted_salary_range"].apply(parse_salary).tolist()
    )
    df_combined["salary_min"] = pd.to_numeric(
        df_combined["salary_min"], errors="coerce"
    )
    df_combined["salary_max"] = pd.to_numeric(
        df_combined["salary_max"], errors="coerce"
    )
    rules = load_employer_rules()
    df_combined["employer_type"] = df_combined["company"].apply(
        lambda c: classify_employer(c, rules)
    )

    return df_combined
