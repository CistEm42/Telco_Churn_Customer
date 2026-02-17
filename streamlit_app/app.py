import streamlit as st
import requests


st.title("Telco Churn Prediction")

st.write("Enter the Customer data to predict Churn: ")

gender = st.selectbox("Gender", ["Male", "Female"])
senior_citizen = st.selectbox("Senior Citizen", [0, 1])
partner = st.selectbox("Partner", [0, 1])
dependents = st.selectbox("Dependents", [0, 1])
tenure = st.number_input("Tenure", min_value=0, value=12)
monthly_charges = st.number_input("Monthly Charges", min_value=0.0, value=70.0)
total_charges = st.number_input("Total Charges", min_value=0.0, value=2000.0)
internet_service = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No"])
contract = st.selectbox("Contract", ["Month-to-Month", "One year", "Two year"])
payment_method = st.selectbox("Payment Method", ["Electronic check", "Mailed check", "Bank transfer", "Credit card"])
phone_service = st.selectbox("Phone Service", [0,1])
multiple_lines = st.selectbox("Multiple Lines", ["Yes", "No", "No phone service"])
online_security = st.selectbox("Online Security", ["Yes", "No", "No online security"])
online_backup = st.selectbox("Online Backup", ["Yes", "No", "No online backup"])
device_protection = st.selectbox("Device Protection", ["Yes", "No", "No device protection"])
tech_support = st.selectbox("Tech Support", ["Yes", "No", "No tech support"])
streaming_tv = st.selectbox("Streaming TV", ["Yes", "No", "No streaming tv"])
streaming_movies = st.selectbox("Streaming Movies", ["Yes", "No", "No streaming movies"])
paperless_billing = st.selectbox("Paperless Billing", [0,1])


if st.button("Predict Churn"):
    payload = {
    "gender": gender,
    "SeniorCitizen": senior_citizen,
    "Partner": partner,
    "Dependents": dependents,
    "tenure": tenure,
    "PhoneService": phone_service,
    "MultipleLines": multiple_lines,
    "InternetService": internet_service,
    "OnlineSecurity": online_security,
    "OnlineBackup": online_backup,
    "DeviceProtection": device_protection,
    "TechSupport": tech_support,
    "StreamingTV": streaming_tv,
    "StreamingMovies": streaming_movies,
    "PaperlessBilling": paperless_billing,
    "Contract": contract,
    "PaymentMethod": payment_method,
    "MonthlyCharges": monthly_charges,
    "TotalCharges": total_charges
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