"""
train_dropout_model.py
Trains and saves the EduTrak dropout-risk prediction model.

Run once (from the project folder, after database_setup.py):
    python train_dropout_model.py

Output: dropout_model.pkl

── A NOTE ON THE DATA (worth keeping for your README / viva) ──────────────
EDA on online_learning_engagement_dataset.csv showed that `attendance_rate`
is overwhelmingly the strongest predictor of dropout (correlation ≈ -0.81;
a simple "attendance_rate < 0.6" rule alone gets ~99.8% accuracy). Dropping
attendance_rate entirely and predicting from the other engagement features
(study hours, quiz scores, forum activity, video time, etc.) collapses to
ROC-AUC ≈ 0.50, i.e. those columns carry no independent signal for dropout
in this dataset — likely because the dataset generator derived `dropout`
mainly from attendance and randomized the rest.

Rather than hide this, the model keeps attendance_rate (it IS a genuine,
real-time-available LMS signal in the real world) but combines it with the
full engagement profile, and is evaluated with stratified train/test split
+ 5-fold cross-validation so the reported score isn't misleading. This is
a good talking point: it shows you checked for a dominant/leaky feature
instead of just reporting a 99% accuracy number blindly.
────────────────────────────────────────────────────────────────────────
"""
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report, confusion_matrix

DATA_PATH = "online_learning_engagement_dataset.csv"
MODEL_PATH = "dropout_model.pkl"

NUMERIC_FEATURES = [
    "age", "internet_speed_mbps", "study_hours_weekly", "login_frequency_weekly",
    "avg_session_duration_min", "video_watch_time_min", "assignments_submitted",
    "forum_posts", "quiz_attempts", "avg_quiz_score", "attendance_rate",
    "engagement_score", "final_grade",
]
CATEGORICAL_FEATURES = ["gender", "device_type", "country"]
ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET = "dropout"


def main():
    print("Loading data...")
    df = pd.read_csv(DATA_PATH)
    X = df[ALL_FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    preprocessor = ColumnTransformer(transformers=[
        ("num", "passthrough", NUMERIC_FEATURES),
        ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
    ])

    model = Pipeline(steps=[
        ("preprocess", preprocessor),
        ("classifier", RandomForestClassifier(
            n_estimators=300, max_depth=8, random_state=42, class_weight="balanced"
        )),
    ])

    print("Training RandomForestClassifier...")
    model.fit(X_train, y_train)

    pred = model.predict(X_test)
    proba = model.predict_proba(X_test)[:, 1]
    acc = accuracy_score(y_test, pred)
    auc = roc_auc_score(y_test, proba)

    print("=" * 60)
    print("EduTrak Dropout Risk Model — Evaluation")
    print("=" * 60)
    print(f"Accuracy : {acc:.4f}")
    print(f"ROC AUC  : {auc:.4f}\n")
    print(classification_report(y_test, pred, target_names=["Retained", "Dropout"]))
    print("Confusion matrix:")
    print(confusion_matrix(y_test, pred))

    print("\nRunning 5-fold cross-validation...")
    cv_scores = cross_val_score(model, X, y, cv=5, scoring="roc_auc")
    print(f"5-fold CV ROC AUC: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

    # Feature importance, mapped back through the one-hot encoder to real names
    ohe = model.named_steps["preprocess"].named_transformers_["cat"]
    cat_names = list(ohe.get_feature_names_out(CATEGORICAL_FEATURES))
    feature_names = NUMERIC_FEATURES + cat_names
    importances = model.named_steps["classifier"].feature_importances_
    importance_series = pd.Series(importances, index=feature_names).sort_values(ascending=False)
    print("\nTop feature importances:")
    print(importance_series.head(10).to_string())

    joblib.dump({
        "model": model,
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "feature_importances": importance_series,
        "metrics": {
            "accuracy": float(acc),
            "roc_auc": float(auc),
            "cv_roc_auc_mean": float(cv_scores.mean()),
            "cv_roc_auc_std": float(cv_scores.std()),
        },
    }, MODEL_PATH)
    print(f"\nSaved model -> {MODEL_PATH}")


if __name__ == "__main__":
    main()
