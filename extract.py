from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

file_path = BASE_DIR / "data" / "Washington_Job_tracker_v2_9_19_1.xlsx"

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
    assert len(df_combined) == 40, f"expected 40 rows, got {len(df_combined)}"
    return df_combined

if __name__ == "__main__":
    df = load_tracker(file_path)
    print(df.columns.tolist())

