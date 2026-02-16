import pandas as pd
from pathlib import Path

RAW_PATH = Path("C:/Users/Durosimi/PROJECTS/Churn/data/Telco_Customer_Churn.csv")

def extract():
    data = pd.read_csv(RAW_PATH)
    print(f"[EXTRACT] Rows: {data.shape[0]}, Columns: {data.shape[1]}")
    return data


if __name__ == "__main__":
    extract()