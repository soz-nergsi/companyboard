import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

st.set_page_config("Monthly Company Dashboard", layout="wide")
st.title("Monthly Company Dashboard")

# Embedded data from your real CSVs
# Revenue Data
revenue_data = {
    'DATE': ['February', 'February', 'February'],
    'Customer': ['Gasin', 'TCC', 'Kawa'],
    'Amount': [200.0, 900.0, 100.0]
}
revenue_df = pd.DataFrame(revenue_data)

# Supply Chain Data
supplychain_data = {
    'Job Order': ['SPH91', 'SPH77', 'SPH66', 'SPH17', 'SPH11'],
    'PR': pd.to_datetime(['1/5/2025', '2/8/2025', '3/4/2025', '4/30/2025', '5/27/2025'], format='%m/%d/%Y'),
    'PO': pd.to_datetime(['1/20/2025', '2/28/2025', '4/15/2025', '5/15/2025', '6/1/2025'], format='%m/%d/%Y')
}
supplychain_df = pd.DataFrame(supplychain_data)

# Sales Data
sales_data = {
    'Job Order': ['s1', 's2', 's3', 's4', 's5'],
    'Customer': ['Seven Net', 'Azo Fashion', 'Asia Pay', 'eklam', 'FIG'],
    'Amount': [100.0, 200.0, 900.0, 500.0, 44.0]
}
sales_df = pd.DataFrame(sales_data)

# Sidebar menu
menu = ["Finance Revenue", "Supply Chain", "Sales"]
choice = st.sidebar.selectbox("Select Dashboard", menu)

if choice == "Finance Revenue":
    st.header("Finance Revenue Dashboard")

    # Pie Chart: Customer Rate
    st.subheader("Customer Rate")
    below_200 = revenue_df[revenue_df['Amount'] <= 200].shape[0]
    above_200 = revenue_df[revenue_df['Amount'] > 200].shape[0]
    labels = ['<= $200', '> $200']
    sizes = [below_200, above_200]
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    st.pyplot()

    # Pie Chart: Revenue Impact
    st.subheader("Revenue Impact")
    min_revenue = revenue_df['Amount'].min()
    total_revenue = revenue_df['Amount'].sum()
    other_revenue = total_revenue - min_revenue
    labels = ['Minimum Revenue', 'Other Revenue']
    sizes = [min_revenue, other_revenue]
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    st.pyplot()

    # Add New Data
    st.subheader("Add New Finance Revenue Data")
    with st.form("finance_form"):
        date = st.text_input("Month (e.g., February)")
        customer = st.text_input("Customer Name")
        amount = st.number_input("Amount", min_value=0.0)
        submit = st.form_submit_button("Add Record")
        if submit:
            new_row = pd.DataFrame({"DATE": [date], "Customer": [customer], "Amount": [amount]})
            revenue_df = pd.concat([revenue_df, new_row], ignore_index=True)
            st.success("Data has been added successfully!")

elif choice == "Supply Chain":
    st.header("Supply Chain Dashboard")

    st.subheader("Job Order Duration")
    supplychain_df['Duration'] = (supplychain_df['PO'] - supplychain_df['PR']).dt.days
    df_sorted = supplychain_df.sort_values('PR')
    plt.fill_between(df_sorted['PR'].dt.strftime('%Y-%m-%d'), df_sorted['Duration'], step="pre", alpha=0.4)
    plt.plot(df_sorted['PR'].dt.strftime('%Y-%m-%d'), df_sorted['Duration'], drawstyle='steps-pre')
    plt.xticks(rotation=45)
    plt.ylabel("Duration (Days)")
    plt.xlabel("PR Date")
    plt.title("Supply Chain Duration")
    st.pyplot()

    # Add New Data
    st.subheader("Add New Supply Chain Data")
    with st.form("supply_form"):
        job_order = st.text_input("Job Order")
        pr_date = st.date_input("PR Date")
        po_date = st.date_input("PO Date")
        submit = st.form_submit_button("Add Record")
        if submit:
            new_row = pd.DataFrame({"Job Order": [job_order], "PR": [pr_date], "PO": [po_date]})
            supplychain_df = pd.concat([supplychain_df, new_row], ignore_index=True)
            st.success("Data has been added successfully!")

elif choice == "Sales":
    st.header("Sales Dashboard")

    st.subheader("Sales Summary")
    num_orders = sales_df.shape[0]
    unique_customers = sales_df['Customer'].nunique()
    total_amount = sales_df['Amount'].sum()

    summary_df = pd.DataFrame({
        "Metric": ["Number of Orders", "Number of Unique Customers", "Total Amount ($)"],
        "Value": [num_orders, unique_customers, total_amount]
    })
    st.table(summary_df)

    # Add New Data
    st.subheader("Add New Sales Data")
    with st.form("sales_form"):
        job_order = st.text_input("Job Order")
        customer = st.text_input("Customer Name")
        amount = st.number_input("Amount", min_value=0.0)
        submit = st.form_submit_button("Add Record")
        if submit:
            new_row = pd.DataFrame({"Job Order": [job_order], "Customer": [customer], "Amount": [amount]})
            sales_df = pd.concat([sales_df, new_row], ignore_index=True)
            st.success("Data has been added successfully!")
