import streamlit as st
import pandas as pd
import sys
import os

# ----------------------------------------
# 📦 Relative Import (works on Streamlit Cloud)
# ----------------------------------------
from services.pdf_parser import parse_pdf
from services.expense_classifier import classify_transactions

# ----------------------------------------
# 🎨 Streamlit UI Setup
# ----------------------------------------
st.set_page_config(page_title="ML Expense Categorizer", layout="wide")
st.title("💳 ML Expense Categorization App")
st.markdown(
    "Upload a **bank or credit card PDF**, and this app will extract and categorize your expenses using machine learning."
)

# ----------------------------------------
# 📤 File Upload
# ----------------------------------------
uploaded_file = st.file_uploader("📄 Upload your PDF statement", type=["pdf"])

if uploaded_file:
    with st.spinner("🔍 Parsing and processing your file..."):
        try:
            # Step 1: Parse PDF into transaction DataFrame
            transactions_df = parse_pdf(uploaded_file)

            if transactions_df.empty:
                st.warning("⚠️ No transactions were extracted. Please check the PDF format.")
            else:
                # Step 2: Run ML classification
                result_df = classify_transactions(transactions_df)

                # 🔍 Debug Output
                st.write("✅ Preview of Parsed + Classified Transactions")
                st.dataframe(result_df)

                # Step 3: Check if result_df is valid before download
                if not result_df.empty:
                    csv = result_df.to_csv(index=False).encode("utf-8")

                    # Step 4: Download Button
                    st.download_button(
                        label="⬇️ Download Categorized Transactions",
                        data=csv,
                        file_name="categorized_expenses.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("⚠️ No results to download. Check if 'Description' column was parsed correctly.")
        except Exception as e:
            st.error(f"❌ An error occurred during processing:\n\n{e}")
else:
    st.info("📥 Please upload a PDF file to begin.")
