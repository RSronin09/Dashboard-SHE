import fitz  # PyMuPDF
import pandas as pd
import re


def parse_pdf_text(uploaded_file):
    """Extract all text lines from the uploaded PDF file using PyMuPDF."""
    pdf_lines = []
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            text = page.get_text()
            lines = text.split("\n")
            pdf_lines.extend(lines)
    return pdf_lines


def classify_transaction(description, amount_str):
    """Determine if the transaction is a Purchase, Credit, or Debt."""
    try:
        amount = float(amount_str)
    except ValueError:
        return "Unknown"

    if amount < 0:
        return "Credit"

    debt_keywords = [
        "fee", "interest", "advance", "charge", "penalty", "late", "finance"
    ]
    if any(keyword in description.lower() for keyword in debt_keywords):
        return "Debt"

    return "Purchase"


def extract_transactions_from_text(lines):
    """
    Enhanced transaction parser:
    - Tracks cardholder changes
    - Handles multi-line descriptions
    - Extracts sale date, post date, description, amount
    - Adds Transaction Type classification
    """
    transactions = []
    current_cardholder = None
    i = 0

    def is_date(s):
        return bool(re.match(r"\d{2}/\d{2}", s.strip()))

    while i < len(lines):
        line = lines[i].strip()

        # Track current cardholder
        if "LAURO R SERRANO" in line:
            current_cardholder = "Lauro R Serrano"
            i += 1
            continue
        elif "CARLOS RIVERA" in line:
            current_cardholder = "Carlos Rivera"
            i += 1
            continue

        # Try to parse a transaction block
        if i + 3 < len(lines) and is_date(lines[i]) and is_date(lines[i + 1]):
            sale_date = lines[i].strip()
            post_date = lines[i + 1].strip()
            description_lines = []
            j = i + 2

            # Collect all lines until a line ends in a dollar amount
            while j < len(lines):
                amount_match = re.search(r"\$[\d,]+\.\d{2}", lines[j])
                if amount_match:
                    amount_str = amount_match.group().replace("$", "").replace(",", "").strip()
                    break
                description_lines.append(lines[j].strip())
                j += 1
            else:
                i += 1
                continue  # no amount found, skip

            description = " ".join(description_lines).strip()
            txn_type = classify_transaction(description, amount_str)

            transactions.append({
                "Sale Date": sale_date,
                "Post Date": post_date,
                "Description": description,
                "Amount": amount_str,
                "Cardholder": current_cardholder,
                "Transaction Type": txn_type
            })

            i = j + 1
        else:
            i += 1

    return pd.DataFrame(transactions)


def parse_pdf(uploaded_file):
    """Wrapper for full pipeline: parse text + extract transactions."""
    lines = parse_pdf_text(uploaded_file)
    df = extract_transactions_from_text(lines)
    return df
