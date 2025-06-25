import streamlit as st
import pandas as pd
import os

SALES_FILE = 'sales_data.csv'
SALES_COLUMNS = ['Job Order', 'Customer', 'Amount']

def initialize_file():
    if not os.path.exists(SALES_FILE):
        pd.DataFrame(columns=SALES_COLUMNS).to_csv(SALES_FILE, index=False)

initialize_file()

def load_data():
    return pd.read_csv(SALES_FILE)

def save_data(df):
    df.to_csv(SALES_FILE, index=False)

def render():
    st.subheader("🛒 Sales Dashboard")

    df = load_data()
    st.dataframe(df, use_container_width=True)

    if not df.empty:
        # Ensure Amount column is numeric
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)

        total_orders = len(df)
        unique_customers = df['Customer'].nunique()
        total_sales = df['Amount'].sum()

        # Create summary table
        summary = {
            "Metric": ["Total Orders", "Unique Customers", "Total Sales"],
            "Value": [total_orders, unique_customers, f"${total_sales:,.2f}"]
        }
        summary_df = pd.DataFrame(summary)

        st.markdown("### 📊 Sales Summary")
        st.table(summary_df)

    #### Add new entry form ####
    st.markdown("### ➕ Add New Sales Entry")
    with st.form("add_sales"):
        job_order = st.text_input("Job Order")
        customer = st.text_input("Customer")
        amount = st.text_input("Amount (numeric)")
        submit = st.form_submit_button("Add Sales Entry")
        if submit:
            try:
                amount_float = float(amount)
                new_row = pd.DataFrame([[job_order, customer, amount_float]], columns=SALES_COLUMNS)
                updated_df = pd.concat([pd.read_csv(SALES_FILE), new_row], ignore_index=True)
                save_data(updated_df)
                st.success("Sales entry added!")
                st.rerun()
            except:
                st.error("Please enter a valid numeric amount!")
