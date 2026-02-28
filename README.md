- Customer Churn Prediction App

A full-stack machine learning application that predicts customer churn using:

FastAPI (Model API)

Streamlit (Frontend UI)

Docker & Docker Compose (Containerization)

Scikit-Learn (ML model)

- Project Overview

This project predicts whether a telecom customer is likely to churn based on service usage, billing details, and contract information.

The system is split into:

API Service → Handles model inference

Web Service → User interface built with Streamlit

Docker Compose → Orchestrates both services

- How It Works

User enters customer details in Streamlit UI

Streamlit sends POST request to FastAPI

FastAPI loads trained model

Model returns:

prediction (0 or 1)

churn_probability

UI displays results

- Running with Docker (Recommended)
-- Prerequisites

Install Docker Desktop

Make sure Docker Engine is running