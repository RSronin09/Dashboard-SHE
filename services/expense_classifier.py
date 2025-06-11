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
    Expects a DataFrame with at least a 'Description' column.
    Returns the original DataFrame with an added 'Predicted_GL' column.
    """
    if "Description" not in transactions_df.columns:
        raise ValueError("❌ 'Description' column is required in the input DataFrame.")

    # Make predictions using the trained pipeline
    try:
        predicted_gl = model.predict(transactions_df["Description"])
        transactions_df["Predicted_GL"] = predicted_gl
    except Exception as e:
        raise RuntimeError(f"❌ Error during classification: {e}")

    return transactions_df
