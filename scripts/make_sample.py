from pathlib import Path

from pandas import ExcelWriter

import pandas as pd

COLUMNS = ["Job Title", "Company", "Req #", "Date Submitted", "Posting Close Date", "Posted Salary Range", "Fit Lane", "Application Status", "Days Since Submitted", "Next Steps / Action Items", "Notes"]

ACTIVE_DATA = [
    {
        "Job Title": "Engineer",
        "Company": "Wayne Enterprises",
        "Req #": "2026-102626",
        "Date Submitted": "10/25/2026",
        "Posting Close Date": "11/05/2026",
        "Posted Salary Range": "$105,000-$125,000",
        "Fit Lane": "Building/Creating",
        "Application Status": "🟡 In Review",
        "Days Since Submitted": "1",
        "Next Steps / Action Items": "Follow up with HR",
        "Notes": "Designing new products for Wayne enterprises"
    },
    {
        "Job Title": "Financial Data Engineer",
        "Company": "The American Red Cross",
        "Req #": "ARC-2026-FDE94",
        "Date Submitted": "2026-10-15",
        "Posting Close Date": "2026-11-05",
        "Posted Salary Range": "$115,000 - $140,000",
        "Fit Lane": "Building/Creating",
        "Application Status": "🟡 In Review",
        "Days Since Submitted": "11",
        "Next Steps / Action Items": "Prepare for technical round focusing on SQL optimizations and automated ledger reconciliation on November 2nd.",
        "Notes": "Remote position. The role focuses on optimizing ETL pipelines converting donor transactional data into audit-ready general ledger entries."
    },
    {
        "Job Title": "Data Analyst / Analytics Engineer (Finance & Operations)",
        "Company": "King County (Department of Metropolitan Services)",
        "Req #": "2026-KC-11840",
        "Date Submitted": "2026-10-24",
        "Posting Close Date": "Continuous",
        "Posted Salary Range": "$42.50 - $56.00 / hour",
        "Fit Lane": "Data Engineering + Public Accounting",
        "Application Status": "Under Review",
        "Days Since Submitted": "2",
        "Next Steps / Action Items": "Monitor the government jobs portal daily for civil service questionnaire updates or status changes.",
        "Notes": "On-site / Hybrid role. Focuses on writing SQL queries and automating pipeline reporting for regional transit asset tracking and public fund allocations."
    },
    {
        "Job Title": "Data Engineer I",
        "Company": "Apex Sound Analytics",
        "Req #": "REQ-1001",
        "Date Submitted": "2026-10-15",
        "Posting Close Date": "2026-11-15",
        "Posted Salary Range": "$105,000 - $125,000",
        "Fit Lane": "Building/Creating",
        "Application Status": "🟡 In Review",
        "Days Since Submitted": 11,
        "Next Steps / Action Items": "Follow up with HR recruiter",
        "Notes": "Focus on Python ETL pipelines and SQL models.",
    },
    {
        "Job Title": "Financial Systems Specialist",
        "Company": "Olympic Health Network",
        "Req #": "FIN-204",
        "Date Submitted": "2026-10-01",
        "Posting Close Date": "Continuous",  # String close date
        "Posted Salary Range": "$75,000 - $95,000 (Target $82,000)",  # Parenthetical range
        "Fit Lane": "Servicing/Administrative",
        "Application Status": " 🟡 In Review  ",  # Messy leading/trailing whitespace
        "Days Since Submitted": 25,
        "Next Steps / Action Items": "Review benefits package",
        "Notes": "Accounting reconciliation and ERP administration.",
    },
    {
        "Job Title": "BI Developer",
        "Company": "Cascade Public Transit",
        "Req #": None,
        "Date Submitted": "2026-09-20",
        "Posting Close Date": None,  # Missing close date
        "Posted Salary Range": "$38.50 - $46.00/hr",  # Hourly range
        "Fit Lane": "Building/Creating",
        "Application Status": "🟡 In Review",
        "Days Since Submitted": 36,  # 30+ days: hits aging query criteria
        "Next Steps / Action Items": "Await initial phone screen",
        "Notes": "Power BI dashboards and SQL reporting.",
    },
    {
        "Job Title": "Integration Analyst",
        "Company": "Puget Tech Solutions",
        "Req #": "PT-8890",
        "Date Submitted": "2026-10-20",
        "Posting Close Date": "2026-11-01",
        "Posted Salary Range": "$115,000",  # Single annual salary value
        "Fit Lane": "Troubleshooting/Support",
        "Application Status": "🟢 Offer",
        "Days Since Submitted": 6,
        "Next Steps / Action Items": "Negotiate start date",
        "Notes": "Full-stack middleware and API integrations.",
    },
    {
        "Job Title": "Operations Data Specialist",
        "Company": "Rainier Logistics Group",
        "Req #": "LOG-312",
        "Date Submitted": "2026-10-10",
        "Posting Close Date": "2026-10-25",
        "Posted Salary Range": None,  # Blank salary
        "Fit Lane": "Servicing/Administrative",
        "Application Status": "🟡 In Review",
        "Days Since Submitted": 16,
        "Next Steps / Action Items": "Pending review",
        "Notes": "Supply chain operations and reporting.",
    },
]

ARCHIVED_DATA = [
    {
        "Job Title": "Analytics Consultant",
        "Company": "Evergreen Health Alliance",
        "Req #": "EH-9901",
        "Date Submitted": "2026-08-15",
        "Posting Close Date": "2026-08-30",
        "Posted Salary Range": "$95,000 - $115,000",
        "Fit Lane": "Building/Creating",
        "Application Status": "⚪ No Longer Considered",
        "Days Since Submitted": 72,
        "Next Steps / Action Items": "N/A - Closed",
        "Notes": "Role filled internally.",
    },
    {
        "Job Title": "Systems Administrator",
        "Company": "Sound Municipal Services",
        "Req #": "SMS-440",
        "Date Submitted": "2026-07-10",
        "Posting Close Date": "Continuous",
        "Posted Salary Range": "$32.00 - $40.00/hr",
        "Fit Lane": "Troubleshooting/Support",
        "Application Status": "⚪ No Longer Considered",
        "Days Since Submitted": 108,
        "Next Steps / Action Items": "Archived",
        "Notes": "Position canceled by department.",
    },
]

# convert lists to DataFrames enforcing COLUMNS schema
df_active = pd.DataFrame(ACTIVE_DATA, columns=COLUMNS)
df_archived = pd.DataFrame(ARCHIVED_DATA, columns=COLUMNS)

# Export using openpyxl engine
target_path = Path("data/sample_tracker.xlsx")

df_active["Date Submitted"] = pd.to_datetime(df_active["Date Submitted"], format="mixed")
df_archived["Date Submitted"] = pd.to_datetime(df_archived["Date Submitted"], format="mixed")

with pd.ExcelWriter(target_path, engine="openpyxl") as writer:
    df_active.to_excel(writer, sheet_name="Active Applications", index=False)
    df_archived.to_excel(writer, sheet_name="Archived Applications", index=False)

print(f"Successfully generated {target_path}")