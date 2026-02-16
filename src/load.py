import pandas as pd
from sqlalchemy import create_engine
from src.extract import extract
from src.transform import transform
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_PATH = OUTPUT_DIR / "Telco_Customer_Churn_clean.csv"

# ---- Ensure directory exists ----
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ENGINE = create_engine(
    r"mssql+pyodbc://DESKTOP-VESV47U\SQLEXPRESS/TelcoChurn"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    "&trusted_connection=yes"
)

def load():
    data_raw = extract()
    data_clean = transform(data_raw)

    # Save clean CSV
    data_clean.to_csv(OUTPUT_PATH, index=False)
    print(f"[LOAD] Clean CSV saved to {OUTPUT_PATH}")

    # Load to SQL Server
    data_clean.to_sql(
        name="TelcoClean",
        schema="dbo",
        con=ENGINE,
        if_exists="replace",
        index=False
    )

    print("[LOAD] Data loaded into SQL Server")

    return data_clean

if __name__ == "__main__":
    load()