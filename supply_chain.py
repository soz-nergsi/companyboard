import streamlit as st
import pandas as pd
import os
from datetime import datetime

SUPPLYCHAIN_FILE = "supply_chain_data.csv"
SUPPLYCHAIN_COLUMNS = ["Job Order", "PR", "PO"]

def initialize_file():
    if not os.path.exists(SUPPLYCHAIN_FILE):
        pd.DataFrame(columns=SUPPLYCHAIN_COLUMNS).to_csv(SUPPLYCHAIN_FILE, index=False)

initialize_file()

def load_data():
    return pd.read_csv(SUPPLYCHAIN_FILE)

def save_data(df):
    df.to_csv(SUPPLYCHAIN_FILE, index=False)

def render():
    st.subheader("🚛 Supply Chain Monthly Dashboard")

    df = load_data()
    st.dataframe(df, use_container_width=True)

    if not df.empty:
        df["PR"] = pd.to_datetime(df["PR"], errors='coerce', dayfirst=False)
        df["PO"] = pd.to_datetime(df["PO"], errors='coerce', dayfirst=False)
        df = df.dropna(subset=["PR", "PO"])

        df["Duration"] = (df["PO"] - df["PR"]).dt.days
        df["Month"] = df["PR"].dt.strftime('%B')

        monthly_summary = df.groupby("Month").agg({
            "Job Order": "count",
            "Duration": "mean"
        }).rename(columns={"Job Order": "Job Orders", "Duration": "Average Days"}).reset_index()

        # Fix month order
        month_order = ["January", "February", "March", "April", "May", "June",
                       "July", "August", "September", "October", "November", "December"]
        monthly_summary["Month"] = pd.Categorical(monthly_summary["Month"], categories=month_order, ordered=True)
        monthly_summary = monthly_summary.sort_values("Month")

        st.markdown("### 📊 Job Orders and Average Duration")
        import matplotlib.pyplot as plt

        fig, ax1 = plt.subplots(figsize=(8, 4))
        ax2 = ax1.twinx()

        ax1.bar(monthly_summary["Month"], monthly_summary["Job Orders"], label="Job Orders", alpha=0.6)
        ax2.plot(monthly_summary["Month"], monthly_summary["Average Days"], color="orange", marker="o", label="Avg Duration (days)")

        ax1.set_ylabel("Job Orders")
        ax2.set_ylabel("Avg Duration (days)")
        ax1.set_xlabel("Month")
        fig.legend(loc="upper left")

        st.pyplot(fig)

    st.markdown("### ➕ Add New Supply Chain Entry")
    with st.form("add_supplychain"):
        job_order = st.text_input("Job Order")
        pr_date = st.date_input("PR Date")
        po_date = st.date_input("PO Date")
        submit = st.form_submit_button("Add Entry")
        if submit:
            new_entry = pd.DataFrame([[job_order, pr_date.strftime('%d/%m/%Y'), po_date.strftime('%d/%m/%Y')]], columns=SUPPLYCHAIN_COLUMNS)
            updated_df = pd.concat([df, new_entry], ignore_index=True)
            save_data(updated_df)
            st.success("Entry added successfully!")
            st.rerun()
