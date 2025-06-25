import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import io

SUPPLYCHAIN_FILE = 'supply_chain_data.csv'
SUPPLYCHAIN_COLUMNS = ['Job Order', 'PR', 'PO']

def initialize_file():
    if not os.path.exists(SUPPLYCHAIN_FILE):
        pd.DataFrame(columns=SUPPLYCHAIN_COLUMNS).to_csv(SUPPLYCHAIN_FILE, index=False)

initialize_file()

def load_data():
    return pd.read_csv(SUPPLYCHAIN_FILE)

def save_data(df):
    df.to_csv(SUPPLYCHAIN_FILE, index=False)

def render():
    st.subheader("🚛 Supply Chain Overview")
    df = load_data()
    st.dataframe(df, use_container_width=True)

    if not df.empty:
        # Convert PR & PO to datetime
        df['PR'] = pd.to_datetime(df['PR'], format='%d/%m/%Y')
        df['PO'] = pd.to_datetime(df['PO'], format='%d/%m/%Y')

        # Calculate Duration
        df['Duration'] = (df['PO'] - df['PR']).dt.days

        # Extract month name from PR
        df['Month'] = df['PR'].dt.strftime('%B')

        # Group by Month
        month_group = df.groupby('Month').agg({
            'Job Order': 'count',
            'Duration': 'mean'
        }).reset_index()

        # Sort months properly
        month_group['Month_num'] = pd.to_datetime(month_group['Month'], format='%B').dt.month
        month_group = month_group.sort_values('Month_num')

        st.markdown(f"**Total Job Orders:** {df.shape[0]}")
        st.markdown(f"**Average Duration (days):** {df['Duration'].mean():.1f}")

        # Plot
        fig, ax1 = plt.subplots(figsize=(6, 4))

        # Column: Job Orders count
        ax1.bar(month_group['Month'], month_group['Job Order'], color='#90caf9')
        ax1.set_xlabel('Month')
        ax1.set_ylabel('Number of Job Orders', color='blue')
        ax1.tick_params(axis='y', labelcolor='blue')

        # Secondary axis: Stepped average duration
        ax2 = ax1.twinx()
        ax2.step(month_group['Month'], month_group['Duration'], where='mid', color='#f48fb1', linewidth=2)
        ax2.fill_between(month_group['Month'], month_group['Duration'], step='mid', color='#f48fb1', alpha=0.3)
        ax2.set_ylabel('Average Duration (days)', color='pink')
        ax2.tick_params(axis='y', labelcolor='pink')

        plt.title("Monthly Job Orders & Average Duration")
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)

        buf = io.BytesIO()
        fig.savefig(buf, format="jpeg", dpi=150, bbox_inches='tight')
        st.download_button("Download Supply Chain Chart", data=buf.getvalue(),
                           file_name="supply_chain_chart.jpeg", mime="image/jpeg")

    #### Form to add new entry ####
    st.markdown("### ➕ Add New Supply Chain Entry")
    with st.form("add_supply"):
        job_order = st.text_input("Job Order")
        pr = st.text_input("PR Date (e.g. 5/1/2025)")
        po = st.text_input("PO Date (e.g. 20/1/2025)")
        submit = st.form_submit_button("Add Supply Entry")
        if submit:
            new_row = pd.DataFrame([[job_order, pr, po]], columns=SUPPLYCHAIN_COLUMNS)
            updated_df = pd.concat([pd.read_csv(SUPPLYCHAIN_FILE), new_row], ignore_index=True)
            save_data(updated_df)
            st.success("Supply chain entry added!")
            st.rerun()
