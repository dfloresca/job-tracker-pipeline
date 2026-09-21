# STATUS (Mon 9/21, 06:10): both sheets combined (40 rows), index reset, sheet-label column added.
# NEXT: 1) snake_case all column names via .str methods on df.columns
#       2) name the sheet column source_sheet (currently Sheet_Name)
#       3) wrap in def load_tracker(path) that returns the DataFrame (no prints/set_option inside)

from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

file_path = BASE_DIR / "data" / "Washington_Job_tracker_v2_9_19_1.xlsx"

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', 0)

df_active = pd.read_excel(file_path, sheet_name="Active Applications")
df_active_sheet = df_active.assign(Sheet_Name="Active Applications")

df_archived = pd.read_excel(file_path, sheet_name="Archived Applications")
df_archived_sheet = df_archived.assign(Sheet_Name="Archived Applications")

df_combined = pd.concat([df_active_sheet, df_archived_sheet], ignore_index=True)
print("Shape: \n", df_combined.shape)
print(df_combined.info())
print(df_combined.index)
