import pandas as pd
from extract import extract

def transform(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()

    data.columns = data.columns.str.strip()

    yes_no_cols = [
        "Partner", "Dependents", "PhoneService",
        "PaperlessBilling", "Churn"
    ]

    for cols in yes_no_cols:
        data[cols] = data[cols].map({"Yes": 1, "No":0})

    data["SeniorCitizen"] = data["SeniorCitizen"].astype(int)

    #NUMERIC COLUMNS TRANSFORMATION
    data["tenure"] = pd.to_numeric(data["tenure"], errors="coerce")
    data["MonthlyCharges"] = pd.to_numeric(data["MonthlyCharges"], errors="coerce")
    data["TotalCharges"] = pd.to_numeric(data["TotalCharges"], errors="coerce")

    #do data quality checks
    print("Transform null values:")
    print(data.isna().sum())

    return data

if __name__ == "__main__":
    print("Run this using load.py")


