from sklearn.pipeline import Pipeline
import joblib
from src.load import load
from sklearn.impute import SimpleImputer
from pathlib import Path
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import  LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from sklearn.metrics import roc_auc_score, classification_report, f1_score, precision_recall_curve
from src.config import (
    TARGET_COLUMN, NUMERICAL_FEATURES, CATEGORICAL_FEATURES, MODEL_PATH
)

def evaluate_models(data):


    X = data.drop(columns=[TARGET_COLUMN])
    y = data[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        stratify=y,
        random_state=42
    )

    scale_pos_weight = len(y_train[y_train == 0]) / len(y_train[y_train == 1])

    preprocessor = ColumnTransformer(transformers=[
        ("num", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ]), NUMERICAL_FEATURES),
         ("cat", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore"))
        ]), CATEGORICAL_FEATURES)
    ])


    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    models = {
        "Logistic Regression": {"model": LogisticRegression(max_iter=100, 
                class_weight="balanced", random_state=42),
                "params": { "model__C": [0.01, 0.1, 1, 10],
                "model__penalty": ["l2"]}},

        "Random Forest": {"model": RandomForestClassifier(class_weight="balanced", random_state=42), 
                "params": { "model__n_estimators": [100, 200],
                    "model__max_depth": [None, 5, 10],
                    "model__min_samples_split": [2, 5]}},
        "XGBoost": {"model": XGBClassifier(scale_pos_weight=scale_pos_weight,
                        random_state=42,
                        eval_metric="logloss"), "params": {"model__n_estimators": [100, 200],
                                    "model__max_depth": [3, 5],
                                    "model__learning_rate": [0.01, 0.1]}}
    }


    best_model = None
    best_score = -1
    best_model_name = None

    for name, mp in models.items():
            pipeline = Pipeline([
                ("preprocessor", preprocessor),
                ("model", mp["model"])
            ]
            )
            print("Running Grid Search for {name}...")

            grid = GridSearchCV(
                pipeline,
                param_grid=mp["params"],
                cv=cv,
                scoring="roc_auc",
                n_jobs=-1
            )

            grid.fit(X_train, y_train)

            y_pred_proba = grid.best_estimator_.predict_proba(X_test)[:, 1]
            test_auc = roc_auc_score(y_test, y_pred_proba)

            print("Best Params:", grid.best_params_)
            print("CV ROC-AUC:", grid.best_score_)
            print("Test ROC-AUC:", test_auc)

            if test_auc > best_score:
                  best_score = test_auc
                  best_model = grid.best_estimator_
                  best_model_name = name

    print(f"\nBest Model: {best_model_name}")
    print("Best Test ROC-AUC:", best_score)

    joblib.dump(best_model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

    return best_model


if __name__ == "__main__":
    data = load()  # or however you're loading
    best_model = evaluate_models(data)
    joblib.dump(best_model, MODEL_PATH)

        

            