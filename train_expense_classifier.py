import os
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# -------------------------
# Configuration
# -------------------------
file_path = "data/expense_training.xlsx"
required_columns = ['Date', 'Description', 'Quick Books GL']
output_model_path = "model/expense_classifier.pkl"

# -------------------------
# Load Excel Sheets
# -------------------------
xl = pd.ExcelFile(file_path)
all_data = []

print(f"📄 Found sheets: {xl.sheet_names}")

for sheet in xl.sheet_names:
    try:
        df = xl.parse(sheet)
        print(f"✅ Parsed: {sheet}, rows: {len(df)}")
        if all(col in df.columns for col in required_columns):
            filtered = df[required_columns].dropna()
            all_data.append(filtered)
        else:
            print(f"⚠️ Skipped {sheet} - missing required columns")
    except Exception as e:
        print(f"❌ Failed to parse {sheet}: {e}")

# -------------------------
# Combine and Prepare
# -------------------------
if not all_data:
    raise ValueError("No valid sheets found for training.")

df_all = pd.concat(all_data, ignore_index=True)

# Clean labels and descriptions
df_all['Quick Books GL'] = df_all['Quick Books GL'].astype(str).str.strip()
df_all['Description'] = df_all['Description'].astype(str).str.strip()

X = df_all['Description']
y = df_all['Quick Books GL']

# -------------------------
# Train/Test Split
# -------------------------
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# -------------------------
# Build & Train Pipeline
# -------------------------
pipeline = Pipeline([
    ('vectorizer', TfidfVectorizer(ngram_range=(1, 2), stop_words="english")),
    ('classifier', LogisticRegression(max_iter=1000, class_weight="balanced"))
])

pipeline.fit(X_train, y_train)
accuracy = pipeline.score(X_test, y_test)

print(f"✅ Model trained. Accuracy on test set: {accuracy:.2%}")

# -------------------------
# Save Model
# -------------------------
os.makedirs("model", exist_ok=True)
joblib.dump(pipeline, output_model_path)
print(f"✅ Model saved to {output_model_path}")
