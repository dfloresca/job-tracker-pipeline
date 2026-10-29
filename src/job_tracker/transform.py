import logging
import re

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

HOURS_PER_YEAR = 2080


def classify_employer(company, rules):
    c = str(company).lower()
    if c.startswith(tuple(rules["public"])):
        return "public"
    if c.startswith(tuple(rules["nonprofit"])):
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
        "Under Review": "in_review",
        "Under SME Review": "sme_review",
        "SME Review": "sme_review",
        "HR Review": "hr_review",
        "Panel Review": "panel_review",
        "Offer": "offer",
        "No Response": "no_response",
        "Rejected": "rejected",
        "No Longer Considered": "no_longer_considered",
        "Interview Scheduled": "interview_scheduled",
        "Interview Completed": "interview_completed",
    }
    cleaned = series.str.strip().str.replace(r"[^\w\s]", "", regex=True).str.strip()
    mapped = cleaned.map(mapping)
    unmapped_mask = mapped.isna() & cleaned.notna()
    if unmapped_mask.any():
        raise ValueError(
            f"Unmapped status values: {cleaned[unmapped_mask].unique().tolist()}"
        )
    return mapped


def classify_close_date(series):
    """Classify the posting_close_date column into three categories: 'dated', 'continuous', and 'unknown'."""
    # clean strings while keeping the original series intact to detect nulls
    is_unknown = series.isna()
    cleaned = series.astype(str).str.strip().str.lower()

    # define the explicit condititions
    is_continuous = cleaned == "continuous"

    # Match conditions to the choices
    conditions = [is_continuous, is_unknown]
    choices = ["continuous", "unknown"]
    result = np.select(conditions, choices, default="dated")
    return pd.Series(
        pd.Categorical(result), index=series.index, name="close_date_status"
    )


def extract_first_range(text):
    # Strip anything in parenthesis first so it can't interfere
    no_parens = re.sub(r"\(.*?\)", "", text)
    pattern = r"\$\s*(\d[\d,]*(?:\.\d+)?)"
    numbers = re.findall(pattern, no_parens)
    return numbers[:2]  # first two numbers found = the primary range


def detect_pay_basis(text):
    # return 'hourly' if the raw string indicates an hourly rate, else 'annual'
    # first make the text lowercase for case-insensitive matching
    text_lower = text.lower()
    # check for keywords that indicate an hourly rate
    if any(keyword in text_lower for keyword in ["/hr", "/hour", "per hour", "hourly"]):
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
