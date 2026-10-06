# STATUS (10/6): schema.sql written -- applications table (UNIQUE on company/job_title/
# date_submitted) and status_history table (FK to applications.id) both done.
# classify_employer() written as a standalone function, NOT yet wired into load_tracker()
# or tested against the real company list.
# NEXT: 1) add employer_type TEXT to applications table in schema.sql to match
#       2) THEN start Session 9: write the Python that creates tracker.db from schema.sql
#          and inserts df_combined into it

import re
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

file_path = BASE_DIR / "data" / "Washington_Job_tracker_v2_9_19_1.xlsx"

HOURS_PER_YEAR = 2080

def classify_employer(company):
    c = company.lower()
    if c.startswith(("king county", "city of seattle", "port of seattle", "snohomish county pud", "sound transit")):
        return "public"
    if c.startswith(("archdiocese", "providence", "fred hutchinson", "kaiser permanente", "premera blue cross", "cambia")):
        return "nonprofit"
    else:
        return "private"

def normalize_status(series):
    """
    Strip whitespace and emojis from the application_status column, then map to canonical values 
    """
    mapping = {
        "Application Received": "application_received",
        "In Review": "in_review",
        "Under SME Review": "sme_review",
        "SME Review": "sme_review",
        "HR Review": "hr_review",
        "Panel Review": "panel_review",
        "No Response": "no_response",
        "Rejected": "rejected",
        "No Longer Considered": "no_longer_considered",
        "Interview Scheduled": "interview_scheduled",
        "Interview Completed": "interview_completed",
    }
    cleaned = (
        series.str.strip()
        .str.replace(r"[^\w\s]", "", regex=True)
        .str.strip()
    )
    mapped = cleaned.map(mapping)
    unmapped_mask = mapped.isna() & cleaned.notna()
    if unmapped_mask.any():
        raise ValueError(f"Unmapped status values: {cleaned[unmapped_mask].unique().tolist()}")
    return mapped
    
def classify_close_date(series):
    """Classify the posting_close_date column into three categories: 'dated', 'continuous', and 'unknown'."""
    # clean strings while keeping the original series intact to detect nulls
    is_unknown = series.isna()
    cleaned = series.astype(str).str.strip().str.lower()

    # define the explicit condititions
    is_continuous = cleaned == "continuous"
  
    #Match conditions to the choices
    conditions = [
        is_continuous,
        is_unknown
    ]
    choices = ["continuous", "unknown"]
    result =  np.select(conditions, choices, default="dated")
    return pd.Series(pd.Categorical(result), index=series.index, name="close_date_status")

def extract_first_range(text):
    # Strip anything in parenthesis first so it can't interfere
    no_parens = re.sub(r"\(.*?\)", "", text)
    numbers = re.findall(r"[\d,]+\.?\d*", no_parens)
    return numbers[:2] # first two numbers found = the primary range

def detect_pay_basis(text):
    # return 'hourly' if the raw string indicates an hourly rate, else 'annual'
    # first make the text lowercase for case-insensitive matching
    text_lower = text.lower()
    # check for keywords that indicate an hourly rate
    if any(keyword in text_lower for keyword in ["hr"]):
        return "hourly"
    else:
        return "annual"

def parse_salary(text):
    """Return (salary_min, salary_max, salary_pay_basis) parsed from raw salary string."""
    if pd.isna(text):
        return (None, None, None)

    numbers = extract_first_range(text)
    if len(numbers) == 1:
        low = high = numbers[0]
    elif len(numbers) == 2:
        low, high = numbers
    else:
        raise ValueError(f"Expected 1 or 2 numbers, got {numbers!r} from: {text!r}")

    low = float(re.sub(r"[^\d.]", "", low))
    high = float(re.sub(r"[^\d.]", "", high))
    basis = detect_pay_basis(text)

    if basis == "hourly":
        low *= HOURS_PER_YEAR
        high *= HOURS_PER_YEAR

    return low, high, basis

def load_tracker(path):
    df_active = pd.read_excel(path, sheet_name= "Active Applications").assign(source_sheet="Active Applications")
    df_archived = pd.read_excel(path, sheet_name= "Archived Applications").assign(source_sheet="Archived Applications")
    df_combined = pd.concat([df_active, df_archived], ignore_index=True)
    df_combined.columns = (
        df_combined.columns.astype(str)
        .str.replace(r"[^\w\s]", " ", regex=True)
        .str.strip()
        .str.replace(r"\s+", "_", regex=True)
        .str.lower()
        )
    df_combined["application_status"] = normalize_status(df_combined["application_status"])
    df_combined["close_date_status"] = classify_close_date(df_combined["posting_close_date"])
    df_combined["posting_close_date"] = pd.to_datetime(df_combined["posting_close_date"], errors="coerce")
    df_combined["date_submitted"] = pd.to_datetime(df_combined["date_submitted"], errors="coerce")
    # compute days_since_submitted as the difference between now and date_submitted normalizeing times for consistency
    df_combined["days_since_submitted"] = (pd.Timestamp.now().normalize() - df_combined["date_submitted"]).dt.days
    # parse the salary range into min, max, and pay basis columns
    df_combined[["salary_min", "salary_max", "salary_pay_basis"]] =(df_combined["posted_salary_range"].apply(parse_salary).tolist())
    df_combined["salary_min"] = pd.to_numeric(df_combined["salary_min"], errors="coerce")
    df_combined["salary_max"] = pd.to_numeric(df_combined["salary_max"], errors="coerce")
    df_combined["employer_type"] = df_combined["company"].apply(classify_employer)    
    
    assert len(df_combined) == 40, f"expected 40 rows, got {len(df_combined)}"
    return df_combined

if __name__ == "__main__":
    df = load_tracker(file_path)
    #print(df["company"].unique())
    print(df[["company", "employer_type"]])