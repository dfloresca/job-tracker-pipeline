import logging

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = ["company", "job_title", "date_submitted", "application_status"]
# must match schema
KEY_COLUMNS = ["company", "job_title", "date_submitted"]
# columns validate_tracker reads; keep in sync with the checks below
VALIDATED_COLUMNS = (
    REQUIRED_COLUMNS + KEY_COLUMNS + ["salary_min", "salary_max", "source_sheet"]
)


def validate_tracker(df):
    """Raise ValueError listing every problem found; return None if data is clean"""
    problems = []

    # check 0 required columns and at least one row, else stop early
    missing = [col for col in VALIDATED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Tracker is missing required columns: {missing}")
    if df.empty:
        raise ValueError("Tracker has no rows")

    # check 1: required fields are present
    for col in REQUIRED_COLUMNS:
        for i in df.index[df[col].isna()]:
            problems.append(
                f"{df.loc[i, 'source_sheet']}: {col} is missing for {df.loc[i, 'company']} / {df.loc[i, 'job_title']}"
            )

    # check 2 : no duplicates
    for i in df.index[df.duplicated(subset=KEY_COLUMNS, keep=False)]:
        problems.append(
            f"{df.loc[i, 'source_sheet']}: duplicate Application: {df.loc[i, 'company']} / {df.loc[i, 'job_title']} / {df.loc[i, 'date_submitted']}"
        )

    # check 3: salary range is not inverted (rows with no salary compare as False, so they are skipped)
    for i in df.index[df["salary_min"] > df["salary_max"]]:
        problems.append(
            f"{df.loc[i, 'source_sheet']}: salary range is inverted: {df.loc[i, 'company']} / {df.loc[i, 'job_title']} / {df.loc[i, 'salary_min']} > {df.loc[i, 'salary_max']}"
        )

    if problems:
        logger.error("%d validation problem(s) found", len(problems))
        raise ValueError("Tracker validation failed: \n" + "\n".join(problems))
