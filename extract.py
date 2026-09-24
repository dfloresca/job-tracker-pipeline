# STATUS (9/24): normalize_status() done and working. Explored posting_close_date:
# confirmed 3 real states -- 24 real dates, 2 "Continuous", 14 unknown/NaN (not the same
# as Continuous). is_continuous boolean prototype in __main__ works but only covers
# 2 of the 3 states -- need close_date_status categorical (dated/continuous/unknown) instead.
# VS Code autofilled 3 lines (date_submitted/posting_close_date/days_since_submitted)
# in load_tracker() -- commented out, UNREVIEWED, do not trust or commit as-is.
# NEXT: 1) write classify_close_date() as standalone function, same shape as normalize_status()
#       2) move the working conversion logic from __main__ into load_tracker()
#       3) recompute days_since_submitted from date_submitted, don't trust the autofilled line
#       4) add raise-on-unexpected check after conversion

from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

file_path = BASE_DIR / "data" / "Washington_Job_tracker_v2_9_19_1.xlsx"


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
    """df_combined["date_submitted"] = pd.to_datetime(df_combined["date_submitted"])
    df_combined["posting_close_date"] = pd.to_datetime(df_combined["posting_close_date"], errors="coerce")
    df_combined["days_since_submitted"] = (pd.Timestamp.now() - df_combined["date_submitted"]).dt.days"""
    assert len(df_combined) == 40, f"expected 40 rows, got {len(df_combined)}"
    return df_combined

if __name__ == "__main__":
    df = load_tracker(file_path)
    print(df.columns.tolist())
    print("close date: ", df["posting_close_date"])
    print(df["date_submitted"].value_counts())
    print(df["posting_close_date"].value_counts())
    print(df["days_since_submitted"].value_counts())
    df["is_continuous"] = df["posting_close_date"].astype(str).str.strip().str.lower() == "continuous"
    print(df["is_continuous"].value_counts())
    df["posting_close_date"] = pd.to_datetime(df["posting_close_date"], errors="coerce")
    print("IsNA: ", df["posting_close_date"].isna().sum())