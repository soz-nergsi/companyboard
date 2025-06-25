import streamlit as st
import pandas as pd
import os

SALES_FILE = 'sales_data.csv'
SALES_COLUMNS = ['Job Order', 'Customer', 'Amount']

def initialize_file():
    if not os.path.exists(SALES_FILE):
        pd.DataFrame(columns=SALES_COLUMNS).to_csv(SALES_FILE, index=False)

initialize_file()

def clean_amount(val):
    try:
        return float(val.replace('$', '').strip())
    except:
        return 0.0

def load_data():
    df = pd.read_csv(SALES_FILE)
    if not df.empty:
        df['Amount'] = df['Amount'].apply(clean_amount)
    return df

def save_data(df):
    df.to_csv(SALES_FILE, index=False)

def render():
    st.subheader("🛒 Sales Overview")
    df = load_data()
    st.dataframe(df, use_container_width=True)

    if not df.empty:
        st.metric("Total Sales Amount", f"${df['Amount'].sum():,.2f}")

    st.markdown("### ➕ Add New Sales Entry")
    with st.form("add_sales"):
        job_order = st.text_input("Job Order")
        customer = st.text_input("Customer")
        amount = st.number_input("Amount ($)", min_value=0.0, step=0.01)
        submit = st.form_submit_button("Add Sales Entry")
        if submit:
            new_row = pd.DataFrame([[job_order, customer, f"{amount:.2f}$"]], columns=SALES_COLUMNS)
            updated_df = pd.concat([pd.read_csv(SALES_FILE), new_row], ignore_index=True)
            save_data(updated_df)
            st.success("Sales entry added!")
            st.rerun()
