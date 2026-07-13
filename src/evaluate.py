import tempfile
import pandas as pd
import os
from sklearn.pipeline import Pipeline
import joblib
from src.load import load
from sklearn.impute import SimpleImputer
import mlflow
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from sklearn.metrics import roc_auc_score, classification_report, f1_score, precision_score, recall_score, confusion_matrix
from src.config import (
    TARGET_COLUMN, NUMERICAL_FEATURES, CATEGORICAL_FEATURES, MODEL_PATH
)
import warnings
warnings.filterwarnings("ignore")
import logging
logging.basicConfig(level=logging.INFO)

mlflow.enable_system_metrics_logging()
mlflow.sklearn.autolog(disable=False)
mlflow.set_experiment(experiment_name="Telco_eval")
mlflow.set_tracking_uri("http://127.0.0.1:5000")

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
    all_model_results = {}
    
    with mlflow.start_run(run_name="Telco_Run") as parent_run:
        print(f"Parent Run ID: {parent_run.info.run_id}")
        
        mlflow.log_params({
            "train_size": len(X_train),
            "test_size": len(X_test),
            "num_features": X.shape[1],
            "num_numerical": len(NUMERICAL_FEATURES),
            "num_categorical": len(CATEGORICAL_FEATURES),
            "scale_pos_weight": scale_pos_weight,
            "cv_folds": 5,
            "random_state": 42
        })

        models = {
            "Logistic_Regression": {
                "model": LogisticRegression(max_iter=100, class_weight="balanced", random_state=42),
                "params": {
                    "model__C": [0.01, 0.1, 1, 10],
                    "model__penalty": ["l2"]
                }
            },
            "Random_Forest": {
                "model": RandomForestClassifier(class_weight="balanced", random_state=42),
                "params": {
                    "model__n_estimators": [100, 200],
                    "model__max_depth": [None, 5, 10],
                    "model__min_samples_split": [2, 5]
                }
            },
            "XGBoost": {
                "model": XGBClassifier(
                    scale_pos_weight=scale_pos_weight,
                    random_state=42,
                    eval_metric="logloss",
                    use_label_encoder=False,
                    verbosity=0
                ),
                "params": {
                    "model__n_estimators": [100, 200],
                    "model__max_depth": [3, 5],
                    "model__learning_rate": [0.01, 0.1]
                }
            }
        }

        best_model = None
        best_score = -1
        best_model_name = None
        best_run_id = None

        for name, mp in models.items():
            with mlflow.start_run(run_name=f"{name}_GridSearch", nested=True) as model_run:
                print(f"{'='*50}")
                print(f"Running Grid Search for {name}...")
                print(f"{'='*50}")
                print(f"Model Run ID: {model_run.info.run_id}")
                
                pipeline = Pipeline([
                    ("preprocessor", preprocessor),
                    ("model", mp["model"])
                ])

                mlflow.log_params({
                    "model_name": name,
                    "model_type": type(mp["model"]).__name__,
                    "param_grid": str(mp["params"])
                })

                grid = GridSearchCV(
                    pipeline,
                    param_grid=mp["params"],
                    cv=cv,
                    scoring="roc_auc",
                    n_jobs=-1,
                    verbose=1
                )

                grid.fit(X_train, y_train)

                best_estimator = grid.best_estimator_
                y_pred_proba = best_estimator.predict_proba(X_test)[:, 1]
                test_auc = roc_auc_score(y_test, y_pred_proba)
                y_pred = best_estimator.predict(X_test)
                test_f1 = f1_score(y_test, y_pred)
                test_precision = precision_score(y_test, y_pred)
                test_recall = recall_score(y_test, y_pred)

                tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
                test_specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
                test_accuracy = (tp + tn) / (tp + tn + fp + fn)
                
                # Log metrics to child run
                mlflow.log_metric("cv_mean_roc_auc", grid.best_score_)
                mlflow.log_metric("test_roc_auc", test_auc)
                mlflow.log_metric("test_f1_score", test_f1)
                mlflow.log_metric("test_precision", test_precision)
                mlflow.log_metric("test_recall", test_recall)
                mlflow.log_metric("test_specificity", test_specificity)
                mlflow.log_metric("test_accuracy", test_accuracy)
                
                # Log best parameters
                for param_name, param_value in grid.best_params_.items():
                    clean_name = param_name.replace("model__", "")
                    mlflow.log_param(f"best_{clean_name}", param_value)

                # Log the model
                try:
                    mlflow.sklearn.log_model(
                        sk_model=best_estimator,
                        name=f"model_{name}",
                        registered_model_name=f"Telco_{name}",
                        pip_requirements=None
                    )
                except Exception as e:
                    print(f"Warning: Could not log model with sklearn flavor: {e}")
                    # Fallback: Use pyfunc
                    mlflow.pyfunc.log_model(
                        name=f"model_{name}",
                        python_model=best_estimator,
                        registered_model_name=f"Telco_{name}",
                        pip_requirements=None
                    )

                # Log classification report
                report = classification_report(y_test, y_pred, output_dict=True)
                mlflow.log_dict(report, f"classification_report_{name}.json")

                # Store results
                all_model_results[name] = {
                    "cv_roc_auc": grid.best_score_,
                    "test_roc_auc": test_auc,
                    "test_f1": test_f1,
                    "test_precision": test_precision,
                    "test_recall": test_recall,
                    "test_specificity": test_specificity,
                    "test_accuracy": test_accuracy,
                    "best_params": grid.best_params_
                }

                print(f"Best Params: {grid.best_params_}")
                print(f"CV ROC-AUC: {grid.best_score_:.4f}")
                print(f"Test ROC-AUC: {test_auc:.4f}")
                print(f"Test F1 Score: {test_f1:.4f}")

                # Track best model
                if test_auc > best_score:
                    best_score = test_auc
                    best_model = best_estimator
                    best_model_name = name
                    best_run_id = model_run.info.run_id

        # Log all model results to parent run
        print("\nLogging all model results to parent run...")
        print("="*50)
        
        for model_name, results in all_model_results.items():
            prefix = model_name.lower()
            
            # Log metrics with model name prefix
            mlflow.log_metric(f"{prefix}_cv_roc_auc", results["cv_roc_auc"])
            mlflow.log_metric(f"{prefix}_test_roc_auc", results["test_roc_auc"])
            mlflow.log_metric(f"{prefix}_test_f1", results["test_f1"])
            mlflow.log_metric(f"{prefix}_test_precision", results["test_precision"])
            mlflow.log_metric(f"{prefix}_test_recall", results["test_recall"])
            mlflow.log_metric(f"{prefix}_test_specificity", results["test_specificity"])
            mlflow.log_metric(f"{prefix}_test_accuracy", results["test_accuracy"])
            
            print(f"Logged metrics for {model_name} to parent run")

        # Create comparison DataFrame
        if all_model_results:
            comparison_data = {}
            for model_name, results in all_model_results.items():
                comparison_data[model_name] = {
                    "CV_ROC_AUC": results["cv_roc_auc"],
                    "Test_ROC_AUC": results["test_roc_auc"],
                    "Test_F1": results["test_f1"],
                    "Test_Precision": results["test_precision"],
                    "Test_Recall": results["test_recall"],
                    "Test_Specificity": results["test_specificity"],
                    "Test_Accuracy": results["test_accuracy"]
                }
            
            comparison_df = pd.DataFrame(comparison_data).T
            comparison_df.index.name = "Model"
            
            # Log comparison table without tempfile permission issues
            comparison_json = comparison_df.to_json(orient='table', index=True)
            
            # Use log_dict instead of tempfile
            comparison_dict = comparison_df.to_dict()
            mlflow.log_dict(comparison_dict, "model_comparison.json")
            
            # Also save as CSV
            csv_path = "model_comparison.csv"
            comparison_df.to_csv(csv_path)
            mlflow.log_artifact(csv_path)
            os.remove(csv_path)
            
            print("\nModel Comparison:")
            print(comparison_df.round(4))

        # Log best model info to parent run
        if best_model is not None:
            mlflow.log_params({
                "best_model_name": best_model_name,
                "best_test_roc_auc": best_score,
                "best_model_run_id": best_run_id
            })

        # Save and log best model
        if best_model is not None:
            joblib.dump(best_model, MODEL_PATH)
            mlflow.log_artifact(MODEL_PATH)
            
            print(f"\n{'='*50}")
            print(f"Best Model: {best_model_name}")
            print(f"Best Test ROC-AUC: {best_score:.4f}")
            print(f"Model saved to {MODEL_PATH}")
            print(f"MLflow Run ID: {mlflow.active_run().info.run_id}")
            print(f"{'='*50}")
        else:
            print("Warning: No best model was found!")

    return best_model

if __name__ == "__main__":
    data = load()
    best_model = evaluate_models(data)
    if best_model is not None:
        joblib.dump(best_model, MODEL_PATH)
    else:
        print("Warning: No model to save!")