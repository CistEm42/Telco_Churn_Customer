from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import roc_auc_score, classification_report
import mlflow
from src.config import (
    TARGET_COLUMN, 
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES
)

mlflow.set_experiment(experiment_name="Telco_evaluate")
mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.sklearn.autolog(disable=True)

def train_data(data):
    X = data.drop(colums=[TARGET_COLUMN])
    y = data[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    with mlflow.start_run():
        preprocessor = ColumnTransformer(transformers=[
        ( "num", StandardScaler(), NUMERICAL_FEATURES),
        ("cat", OneHotEncoder(), CATEGORICAL_FEATURES)

        ])

        pipeline = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("model", LogisticRegression(max_iter=100, class_weight="balanced", random_state=42))

        ])

        pipeline.fit(X_train, y_train)

        predictions = pipeline.predict(X_test)

        print(classification_report, predictions)

    return pipeline