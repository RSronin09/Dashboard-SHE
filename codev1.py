import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from services.pdf_parser import parse_pdf
from services.expense_classifier import classify_transactions

# ----------------------------------------
# 🎨 Streamlit UI Setup
# ----------------------------------------
st.set_page_config(page_title="ML Expense Categorizer", layout="wide")

st.title("💳 ML Expense Categorization App")
st.markdown(
    "Upload a **bank or credit card PDF**, and this app will extract and categorize your expenses using machine learning. "
    "You can review and edit the categories before downloading your data."
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

                # Step 3: Editable Table for Review
                st.subheader("✏️ Review & Edit Categorization")
                edited_df = st.data_editor(
                    result_df,
                    use_container_width=True,
                    num_rows="dynamic",
                    column_config={
                        "Predicted_GL": st.column_config.TextColumn(
                            label="GL Category",
                            help="Edit this value to correct or reassign the category"
                        )
                    },
                    hide_index=True
                )

                # Step 4: Pie Chart Visualization
                st.subheader("📊 Expense Breakdown by GL Category")

                try:
                    # Convert Amount column to float
                    edited_df["Amount_float"] = edited_df["Amount"].astype(float)

                    # Only include positive amounts for the pie chart
                    positive_df = edited_df[edited_df["Amount_float"] > 0]

                    pie_data = (
                        positive_df.groupby("Predicted_GL")["Amount_float"]
                        .sum()
                        .reset_index(name="Total")
                    )

                    if pie_data.empty:
                        st.warning("⚠️ No positive expenses to chart.")
                    else:
                        # Display formatted table with dollar signs and commas
                        formatted_data = pie_data.copy()
                        formatted_data["Total"] = formatted_data["Total"].map("${:,.2f}".format)
                        st.dataframe(formatted_data, use_container_width=True)

                        # Plot improved pie chart
                        fig, ax = plt.subplots(figsize=(7, 7))
                        ax.pie(
                            pie_data["Total"],
                            labels=pie_data["Predicted_GL"],
                            autopct="%1.1f%%",
                            startangle=90,
                            labeldistance=1.05,
                            pctdistance=0.75
                        )
                        ax.axis("equal")
                        st.pyplot(fig)

                except Exception as e:
                    st.error(f"❌ Error generating pie chart: {e}")

                # Step 5: CSV Download Button
                st.subheader("⬇️ Download Your Categorized Data")
                download_df = edited_df.drop(columns=["Amount_float"], errors="ignore")
                csv = download_df.to_csv(index=False).encode("utf-8")

                st.download_button(
                    label="Download Categorized Transactions",
                    data=csv,
                    file_name="categorized_expenses.csv",
                    mime="text/csv"
                )

        except Exception as e:
            st.error(f"❌ An error occurred during processing:\n\n{e}")
else:
    st.info("📥 Please upload a PDF file to begin.")
