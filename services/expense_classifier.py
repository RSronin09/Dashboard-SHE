import os
import joblib
import pandas as pd

# Define the relative path to the trained model
model_path = os.path.join("model", "expense_classifier.pkl")

# Load the trained model pipeline
try:
    model = joblib.load(model_path)
except FileNotFoundError:
    raise FileNotFoundError(f"❌ Could not find the model at {model_path}. Make sure it exists and is correctly named.")

def classify_transactions(transactions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Classifies each transaction's GL Category using the trained model.
    Applies override rules for specific known misclassifications.
    """
    if "Description" not in transactions_df.columns:
        raise ValueError("❌ 'Description' column is required in the input DataFrame.")

    predictions = []
    for desc in transactions_df["Description"]:
        desc_lower = str(desc).lower().strip()

        # ✅ Override rule for PAPERSMITH
        if "papersmith" in desc_lower:
            predictions.append("Dues & Subscriptions")
        else:
            try:
                prediction = model.predict([desc])[0]
                predictions.append(prediction)
            except Exception as e:
                predictions.append("Unknown")  # fallback if model fails on this row

    transactions_df["Predicted_GL"] = predictions
    return transactions_df
