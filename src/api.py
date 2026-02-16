from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib
from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parent.parent  / "artifacts" / "model.pkl"
model = joblib.load(MODEL_PATH)

app = FastAPI(title="Telco Churn Prediction API")

#input schema definition using pydantic
class Customer(BaseModel):
        gender: str
        SeniorCitizen: int
        Partner: int
        Dependents: int
        tenure: float
        PhoneService: int
        MultipleLines: str
        InternetService: str
        OnlineSecurity: str
        OnlineBackup: str
        DeviceProtection: str
        TechSupport: str
        StreamingTV: str
        StreamingMovies: str
        Contract: str
        PaperlessBilling: int
        PaymentMethod: str
        MonthlyCharges: float
        TotalCharges: float

@app.get("/")
def read_root():
        return {"message": "Welcome to Telco Churn Prediction"}

@app.post("/predict")
def predict_churn(customer : Customer):
        input_data = pd.DataFrame([customer.model_dump()]) # convert input to data frame

        prob = model.predict_proba(input_data)[:, 1][0]
        prediction = model.predict(input_data)[0]

        return {
            "prediction": int(prediction),  # 1 = churn, 0 = not churn
            "churn_probability": float(prob)
        }