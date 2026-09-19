from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

file_path = BASE_DIR / "data" / "Washington_Job_tracker_v2_9_19_1.xlsx"

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', 0)

df_active = pd.read_excel(file_path, sheet_name="Active Applications")
print("Shape: \n", df_active.shape)
print("Type: \n ", df_active.dtypes)
print("Info: \n", df_active.info())
print("first 5: \n", df_active.head(5))

df_archived = pd.read_excel(file_path, sheet_name="Archived Applications")
print("Shape: \n", df_archived.shape)
print("Type: \n ", df_archived.dtypes)
print("Info: \n", df_archived.info())
print("first 5: \n", df_archived.head(5))