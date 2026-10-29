import pandas as pd

from src.job_tracker.config import TRACKER_PATH

pd.set_option("display.max_columns", None)
pd.set_option("display.max_colwidth", None)
pd.set_option("display.width", 0)

df_active = pd.read_excel(TRACKER_PATH, sheet_name="Active Applications")
print("Shape: \n", df_active.shape)
print("Type: \n ", df_active.dtypes)
print("Info: \n", df_active.info())
print("first 5: \n", df_active.head(5))

df_archived = pd.read_excel(TRACKER_PATH, sheet_name="Archived Applications")
print("Shape: \n", df_archived.shape)
print("Type: \n ", df_archived.dtypes)
print("Info: \n", df_archived.info())
print("first 5: \n", df_archived.head(5))
