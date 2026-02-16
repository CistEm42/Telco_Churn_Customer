from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
RAW_DATA_PATH = DATA_DIR /"C:/Users/Durosimi/PROJECTS/Churn/data/Telco_Customer_Churn.csv"
PROCESSED_DATA_PATH = DATA_DIR / "processed" / "Telco_Customer_Churn_clean.csv"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
ARTIFACTS_DIR = Path(__file__).resolve().parent.parent / "artifacts"
MODEL_PATH = ARTIFACTS_DIR / "model.pkl"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)



YES_NO_COLUMNS = [
    "Partner",
    "Dependents",
    "PhoneService",
    "PaperlessBilling",
    "Churn"
]

NUMERIC_COLUMNS = [
    "tenure",
    "MonthlyCharges",
    "TotalCharges"
]

ID_COLUMNS = ["customerID"]

TARGET_COLUMN = "Churn"

NUMERICAL_FEATURES = [
    "tenure",
    "MonthlyCharges",
    "TotalCharges"
]

CATEGORICAL_FEATURES = [
    "InternetService",
    "Contract",
    "PaymentMethod",
    "MultipleLines",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies"
]

