import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random
from datetime import datetime, timedelta

st.set_page_config(page_title="UPI Monitoring System", layout="wide")

st.title("🏦 UPI Transaction Monitoring System")

# ------------- GENERATE UPI DATA ---------------------
def generate_upi_transactions(n=25):

    banks = ["SBI", "HDFC", "ICICI", "Axis", "PNB"]
    txn_types = ["P2P", "P2M"]

    data = []

    for _ in range(n):
        amount = random.randint(50, 20000)
        sender = f"user{random.randint(1,10)}@okbank"
        receiver = f"merchant{random.randint(1,5)}@paytm"
        bank = random.choice(banks)
        txn_type = random.choice(txn_types)

        random_days = random.randint(0, 10)
        random_hours = random.randint(0, 23)

        txn_time = datetime.now() - timedelta(days=random_days, hours=random_hours)

        data.append([sender, receiver, amount, txn_time, txn_type, bank])

    df = pd.DataFrame(
        data,
        columns=["sender_vpa", "receiver_vpa", "amount", "datetime", "txn_type", "bank"]
    )

    return df


# ------------------- UPI RISK RULES -------------------

def apply_upi_risk_engine(df):

    df["datetime"] = pd.to_datetime(df["datetime"])
    df["risk_score"] = 0

    df.loc[df["amount"] > 15000, "risk_score"] += 40

    df.loc[df["datetime"].dt.hour.isin([0,1,2,3,4]), "risk_score"] += 20

    df.loc[
        (df["txn_type"] == "P2P") &
        (df["amount"] > 10000),
        "risk_score"
    ] += 25
    sender_counts = df["sender_vpa"].value_counts()
    repeated_users = sender_counts[sender_counts >= 4].index
    df.loc[df["sender_vpa"].isin(repeated_users), "risk_score"] += 15
    df["fraud_flag"] = df["risk_score"].apply(lambda x: 1 if x >= 50 else 0)

    return df


# ---------------- DATA SOURCE SELECTION ---------------------
option = st.radio("Choose Data Source", ["Generate Random UPI Data", "Upload CSV File"])

df = None

# ----------------- GENERATE ------------------------
if option == "Generate Random UPI Data":

    if st.button("Generate Transactions"):
        df = generate_upi_transactions()
        df = apply_upi_risk_engine(df)
        st.success("Random UPI dataset generated.")

# ---------------- UPLOAD ---------------------

elif option == "Upload CSV File":

    uploaded_file = st.file_uploader("Upload UPI CSV file", type=["csv"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        df = apply_upi_risk_engine(df)
        st.success("File uploaded and processed.")


# -------------- DISPLAY DATA IF AVAILABLE --------------
if df is not None:

    st.subheader("📄 UPI Transactions")
    st.dataframe(df)

    # -------- SMALL GRAPH --------
    st.subheader("📊 Spending by Bank")

    spending = df.groupby("bank")["amount"].sum()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        fig, ax = plt.subplots(figsize=(3, 2))
        spending.plot(kind="bar", ax=ax)
        ax.set_ylabel("₹ Total")
        ax.set_title("Bank Spending")
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)

    # -------- RISK METRICS --------
    st.subheader("🚨 Risk Summary")

    total_txn = len(df)
    fraud_cases = df["fraud_flag"].sum()
    fraud_percent = round((fraud_cases / total_txn) * 100, 2)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Transactions", total_txn)
    col2.metric("Fraud Cases", fraud_cases)
    col3.metric("Fraud %", f"{fraud_percent}%")

    st.info("""
    Risk Rules:
    • Amount > ₹15000 → +40  
    • 12AM-4AM → +20  
    • P2P > ₹10000 → +25  
    • Same sender ≥ 4 → +15  
    Fraud if risk_score ≥ 50
    """)