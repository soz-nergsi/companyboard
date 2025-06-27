import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import datetime
import os

CSV_FILE = "supply_chain_data.csv"

def load_data():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
    else:
        df = pd.DataFrame(columns=["Job Order", "PR", "PO"])
    return df

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

def render():
    st.subheader("🚛 Supply Chain Monthly Dashboard")

    df = load_data()

    # Parse date and fix duration + month
    df['PR'] = pd.to_datetime(df['PR'], format='%d/%m/%Y', errors='coerce')
    df['PO'] = pd.to_datetime(df['PO'], format='%d/%m/%Y', errors='coerce')
    df['Duration'] = (df['PO'] - df['PR']).dt.days
    df['Month'] = df['PR'].dt.strftime('%B')

    st.dataframe(df)

    # Add new data
    with st.form("add_data"):
        st.markdown("### ➕ Add Supply Chain Entry")
        job_order = st.text_input("Job Order")
        pr = st.text_input("PR Date (DD/MM/YYYY)")
        po = st.text_input("PO Date (DD/MM/YYYY)")
        submit = st.form_submit_button("Add Entry")
        if submit:
            try:
                new_row = pd.DataFrame([[job_order, pr, po]], columns=["Job Order", "PR", "PO"])
                df = pd.concat([df, new_row], ignore_index=True)
                save_data(df)
                st.success("New supply chain entry added.")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    # Dashboard graph
    if not df.empty and 'Month' in df.columns:
        grouped = df.groupby('Month').agg(
            Job_Orders=('Job Order', 'count'),
            Avg_Duration=('Duration', 'mean')
        ).reset_index()

        fig, ax1 = plt.subplots()

        ax2 = ax1.twinx()
        ax1.bar(grouped['Month'], grouped['Job_Orders'], color='lightblue', label='Job Orders')
        ax2.plot(grouped['Month'], grouped['Avg_Duration'], color='green', marker='o', label='Avg Duration')

        ax1.set_xlabel("Month")
        ax1.set_ylabel("Job Orders", color='blue')
        ax2.set_ylabel("Avg Duration (days)", color='green')
        ax1.set_title("Monthly Job Orders and Average Duration")

        st.pyplot(fig)

