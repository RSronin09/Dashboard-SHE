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


def clean_amount(amount_str):
    """Robustly clean and convert string to float."""
    try:
        cleaned = (
            amount_str.replace("(", "-")
                      .replace(")", "")
                      .replace("minus$", "-")
                      .replace("$", "")
                      .replace(",", "")
                      .strip()
        )
        return float(cleaned)
    except Exception as e:
        print(f"[ERROR] Amount parsing failed for: '{amount_str}' -> {e}")
        return 0.0


def classify_transaction(description, amount_str):
    """Determine if the transaction is a Purchase, Credit, or Debt."""
    amount = clean_amount(amount_str)

    if amount < 0:
        return "Credit"

    debt_keywords = [
        "fee", "interest", "advance", "charge", "penalty", "late", "finance"
    ]
    if any(keyword in description.lower() for keyword in debt_keywords):
        return "Debt"

    return "Purchase"


def extract_transactions_from_text(lines):
    transactions = []
    current_cardholder = "General Account"
    i = 0
    in_payments_section = False

    def is_date(s):
        return bool(re.match(r"\d{2}/\d{2}", s.strip()))

    while i < len(lines):
        line = lines[i].strip()

        # Detect section headers
        if "Payments, Credits and Adjustments" in line:
            in_payments_section = True
            i += 1
            continue
        elif "LAURO R SERRANO" in line:
            current_cardholder = "Lauro R Serrano"
            in_payments_section = False
            i += 1
            continue
        elif "CARLOS RIVERA" in line:
            current_cardholder = "Carlos Rivera"
            in_payments_section = False
            i += 1
            continue

        # Payments section: detect 3-line pattern
        if in_payments_section and i + 2 < len(lines):
            date_line = lines[i].strip()
            desc_line = lines[i + 1].strip()
            amount_line = lines[i + 2].strip()

            if is_date(date_line) and "payment" in desc_line.lower() and "minus$" in amount_line.lower():
                sale_date = date_line
                description = desc_line
                amount = amount_line.lower().replace("minus$", "-").replace("$", "").replace(",", "").strip()
                txn_type = classify_transaction(description, amount)

                transactions.append({
                    "Sale Date": sale_date,
                    "Post Date": sale_date,
                    "Description": description,
                    "Amount": amount,
                    "Cardholder": current_cardholder,
                    "Transaction Type": txn_type
                })

                i += 3
                continue

        # Multi-line purchases
        if i + 3 < len(lines) and is_date(lines[i]) and is_date(lines[i + 1]):
            sale_date = lines[i].strip()
            post_date = lines[i + 1].strip()
            description_lines = []
            j = i + 2

            while j < len(lines):
                amount_match = re.search(r"\$[\d,]+\.\d{2}", lines[j])
                if amount_match:
                    amount_str = amount_match.group().strip()
                    break
                description_lines.append(lines[j].strip())
                j += 1
            else:
                i += 1
                continue

            description = " ".join(description_lines).strip()
            txn_type = classify_transaction(description, amount_str)

            transactions.append({
                "Sale Date": sale_date,
                "Post Date": post_date,
                "Description": description,
                "Amount": amount_str.replace("$", "").replace(",", "").strip(),
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
