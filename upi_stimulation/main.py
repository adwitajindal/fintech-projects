import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(page_title="Mini UPI System", layout="wide")

st.title("Mini UPI Payment System")

# ------------ check for json files and create if not exist ------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

USERS_FILE = os.path.join(BASE_DIR, "users.json")
TRANSACTIONS_FILE = os.path.join(BASE_DIR, "transactions.json")
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

if not os.path.exists(TRANSACTIONS_FILE):
    with open(TRANSACTIONS_FILE, "w") as f:
        json.dump([], f)


# ------------ Load users data ------------
with open(USERS_FILE, "r") as f:
    users = json.load(f)


st.sidebar.header("Create New UPI id")

new_user = st.sidebar.text_input("Enter upi id")

if st.sidebar.button("Create User"):
    if new_user in users:
        st.sidebar.error("User already exists")
    elif new_user.strip() == "":
        st.sidebar.error("Username cannot be empty")
    else:
        users[new_user] = {"balance": 0}
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)
        st.sidebar.success("User Created Successfully")
        st.rerun()

# ------------ Load money ------------

st.header("Load Money")

# Check if users exist
user_list = list(users.keys())
if user_list:
    selected_user = st.selectbox("Select User", user_list)
    
    amount = st.number_input("Enter Amount", min_value=1)
    
    if st.button("Add Money"):
        users[selected_user]["balance"] += amount
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)
        st.success("Money Added Successfully")
        st.rerun()
else:
    st.warning("No users found. Please create a user from the sidebar first.")

# ------------ Transfer money ------------

st.header("Transfer Money")

if user_list:
    sender = st.selectbox("Sender", user_list, key="sender")
    receiver = st.selectbox("Receiver", user_list, key="receiver")
    if sender == receiver:
        st.warning("Sender and receiver cannot be the same")
    
    transfer_amount = st.number_input("Transfer Amount", min_value=1, key="transfer")
    
    if st.button("Send Money"):
        if sender == receiver:
            st.error("Sender and receiver cannot be the same")
        elif users[sender]["balance"] >= transfer_amount:
            users[sender]["balance"] -= transfer_amount
            users[receiver]["balance"] += transfer_amount
            with open(TRANSACTIONS_FILE, "r") as f:
                transactions = json.load(f)
            
            transactions.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "from": sender,
                "to": receiver,
                "amount": transfer_amount
            })
            
            with open(TRANSACTIONS_FILE, "w") as f:
                json.dump(transactions, f)
            
            with open(USERS_FILE, "w") as f:
                json.dump(users, f)
            
            st.success("Transaction Successful")
            st.rerun()
        else:
            st.error("Insufficient Balance")
else:
    st.warning("No users found. Please create a user from the sidebar first.")


# ------------ show balances ------------   

st.header("Check Balance")

if user_list:
    selected_user_for_balance = st.selectbox("Select User to Check Balance", user_list, key="balance_user")
    if selected_user_for_balance:
        st.info(f"Current Balance: ₹ {users[selected_user_for_balance]['balance']}")
else:
    st.warning("No users found. Please create a user from the sidebar first.")

# ------------ transaction history ------------

st.header("Transaction History")

with open(TRANSACTIONS_FILE, "r") as f:
    transactions = json.load(f)

if transactions:
    st.table(transactions)
else:
    st.write("No Transactions Yet")