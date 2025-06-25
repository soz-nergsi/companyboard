import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
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
    st.subheader("🚛 Supply Chain - February Only")

    df = load_data()
    st.dataframe(df, use_container_width=True)

    if not df.empty:
        df['PR'] = pd.to_datetime(df['PR'], format='%d/%m/%Y')
        df['PO'] = pd.to_datetime(df['PO'], format='%d/%m/%Y')
        df['Duration'] = (df['PO'] - df['PR']).dt.days

        # ✅ Correct filtering: Use PO month to select February data
        feb_df = df[df['PO'].dt.month == 2]

        # ✅ Count job orders by counting rows
        job_order_count = len(feb_df)
        avg_duration = feb_df['Duration'].mean() if job_order_count > 0 else 0

        st.markdown(f"**Total February Job Orders:** {job_order_count}")
        st.markdown(f"**Average February Duration:** {avg_duration:.1f} days")

        fig, ax1 = plt.subplots(figsize=(6, 5))

        bars = ax1.bar(['February'], [job_order_count], color='#FFEB3B', edgecolor='black')

        if job_order_count > 0:
            ax1.text(0, job_order_count + 0.5, f"{job_order_count} Job Orders",
                     ha='center', va='bottom', fontsize=11, fontweight='bold')

        ax1.set_ylabel('Total Requests', color='black')
        ax1.tick_params(axis='y', labelcolor='black')

        ax2 = ax1.twinx()
        ax2.step(['February'], [avg_duration], where='mid', color='#E91E63', linewidth=3)
        ax2.fill_between(['February'], [0], [avg_duration], step='mid', color='#E91E63', alpha=0.2)
        ax2.set_ylabel('Average Cycle Duration (days)', color='black')
        ax2.tick_params(axis='y', labelcolor='black')

        if avg_duration > 0:
            ax2.text(0, avg_duration + 0.5, f"{avg_duration:.1f} Days",
                     ha='center', va='bottom', fontsize=11, fontweight='bold')

        plt.title("PR Rate & AVG Cycle Duration (February)", fontsize=14, fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)

        buf = io.BytesIO()
        fig.savefig(buf, format="jpeg", dpi=150, bbox_inches='tight')
        st.download_button("Download Chart", data=buf.getvalue(),
                           file_name="february_supply_chain_chart.jpeg", mime="image/jpeg")

    #### Form ####
    st.markdown("### ➕ Add New February Supply Chain Entry")
    with st.form("add_supply"):
        job_order = st.text_input("Job Order")
        pr = st.text_input("PR Date (e.g. 5/2/2025)")
        po = st.text_input("PO Date (e.g. 20/2/2025)")
        submit = st.form_submit_button("Add Supply Entry")
        if submit:
            new_row = pd.DataFrame([[job_order, pr, po]], columns=SUPPLYCHAIN_COLUMNS)
            updated_df = pd.concat([pd.read_csv(SUPPLYCHAIN_FILE), new_row], ignore_index=True)
            save_data(updated_df)
            st.success("Supply chain entry added!")
            st.rerun()
