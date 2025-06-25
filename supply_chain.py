import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
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
        st.metric("Total Orders", len(df))

        df['PR'] = pd.to_datetime(df['PR'], format='%d/%m/%Y')
        df['PO'] = pd.to_datetime(df['PO'], format='%d/%m/%Y')
        df['Duration'] = (df['PO'] - df['PR']).dt.days
        avg_duration = df['Duration'].mean()

        st.markdown("### 📊 Supply Chain Performance")
        fig, ax1 = plt.subplots(figsize=(6, 4))
        ax1.bar(df['Job Order'], df['Duration'], color='skyblue')
        ax1.set_xlabel('Job Orders')
        ax1.set_ylabel('Duration (days)', color='blue')
        ax1.tick_params(axis='y', labelcolor='blue')

        ax2 = ax1.twinx()
        ax2.step(df['Job Order'], [avg_duration]*len(df), where='mid', color='orange', linewidth=2)
        ax2.fill_between(df['Job Order'], [avg_duration]*len(df), step='mid', color='orange', alpha=0.3)
        ax2.set_ylabel('Average Duration', color='orange')
        ax2.tick_params(axis='y', labelcolor='orange')

        plt.title("Job Orders vs. Average Duration")
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)

        buf = io.BytesIO()
        fig.savefig(buf, format="jpeg", dpi=150, bbox_inches='tight')
        st.download_button("Download Supply Chain Chart", data=buf.getvalue(), file_name="supply_chain_chart.jpeg", mime="image/jpeg")

        st.write(f"📊 Average Duration: {avg_duration:.1f} days")

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
