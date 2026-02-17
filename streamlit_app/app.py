import streamlit as st
import requests


st.title("Telco Churn Prediction")

st.write("Enter the Customer data to predict Churn: ")

gender = st.selectbox("Gender", ["Male", "Female"])
senior_citizen = st.selectbox("Senior Citizen", [0,1])
partner = st.selectbox("Partner", [0,1])
dependents = st.selectbox("Dependents", [0,1])
tenure = st.number_input("Tenure", min_value=0, value=12)
monthly_charges = st.number_input("Monthly Charges", min_value=0.0, value=70.0)
total_charges = st.number_input("Total Charges", min_value=0.0, value=2000.0)
internet_service = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No"])
contract = st.selectbox("Contract", ["Month-to-Month", "One year", "Two year"])
payment_method = st.selectbox("Payment Method", ["Electronic check", "Mailed check", "Bank transfer", "Credit card"])


if st.button("Predict Churn"):
    payload = {
        "gender": gender,
        "SeniorCitizen": senior_citizen,
        "Partner": partner,
        "Dependents": dependents,
        "tenure": tenure,
        "MonthlyCharges": monthly_charges,
        "TotalCharges": total_charges,
        "InternetService": internet_service,
        "Contract": contract,
        "PaymentMethod": payment_method
    }

    response = requests.post("http://127.0.0.1:8000/predict", json=payload)

    if response.status_code == 200:
        result = response.json()

        prediction = result["prediction"]
        probability = result["churn_probability"]

        st.success(f"Churn Prediction: {prediction}")
        st.write(f"Churn Probability: {probability:.2%}")
    else:
        st.error(f"Error {response.status_code}")
        st.write(response.text)