import pandas as pd
from src.extract import extract

def transform(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()

    data.columns = data.columns.str.strip()

    yes_no_cols = [
        "Partner", "Dependents", "PhoneService",
        "PaperlessBilling", "Churn"
    ]

    for cols in yes_no_cols:
        data[cols] = data[cols].map({"Yes": 1, "No": 0})

    data["SeniorCitizen"] = data["SeniorCitizen"].astype(int)

    
    data["tenure"] = pd.to_numeric(data["tenure"], errors="coerce")
    data["MonthlyCharges"] = pd.to_numeric(data["MonthlyCharges"], errors="coerce")
    data["TotalCharges"] = pd.to_numeric(data["TotalCharges"], errors="coerce")
    
    
    
    total_charges_median = data["TotalCharges"].median()
    data["TotalCharges"] = data["TotalCharges"].fillna(total_charges_median)
    
    # Also fill any other numeric columns that might have missing values
    data["tenure"] = data["tenure"].fillna(data["tenure"].median())
    data["MonthlyCharges"] = data["MonthlyCharges"].fillna(data["MonthlyCharges"].median())

    # do data quality checks
    print("Transform null values:")
    print(data.isna().sum())

    return data

if __name__ == "__main__":
    print("Run this using load.py")