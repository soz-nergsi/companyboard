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
    try:
        df.to_csv(SUPPLYCHAIN_FILE, index=False)
    except Exception as e:
        raise IOError("❌ Unable to save data. Please connect GitHub repository using Personal Access Token to enable saving data.")

def render():
    st.subheader("🚛 Supply Chain Monthly Dashboard")

    df = load_data()
    st.dataframe(df, use_container_width=True)

    if not df.empty:
        df['PR'] = pd.to_datetime(df['PR'], errors='coerce')
        df['PO'] = pd.to_datetime(df['PO'], errors='coerce')
        df = df.dropna(subset=['PR', 'PO'])
        df['Duration'] = (df['PO'] - df['PR']).dt.days
        df['Month'] = df['PR'].dt.strftime('%B')

        months_full = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
        full_data = pd.DataFrame({'Month': months_full})

        month_group = df.groupby('Month').agg({
            'Job Order': 'count',
            'Duration': 'mean'
        }).reset_index()

        full_data = full_data.merge(month_group, on='Month', how='left').fillna(0)
        full_data['Job Order'] = full_data['Job Order'].astype(int)

        st.markdown(f"**Total Job Orders:** {df.shape[0]}")
        st.markdown(f"**Overall Average Duration:** {df['Duration'].mean():.1f} days")

        fig, ax1 = plt.subplots(figsize=(10, 6))

        bars = ax1.bar(full_data['Month'], full_data['Job Order'], color='#90caf9')

        for bar, count in zip(bars, full_data['Job Order']):
            if count > 0:
                ax1.text(bar.get_x() + bar.get_width()/2, 0.2, f"{count}",
                         ha='center', va='bottom', fontsize=10, fontweight='bold', color='black')

        ax1.set_xlabel('Month')
        ax1.set_ylabel('Job Orders', color='blue')
        ax1.tick_params(axis='y', labelcolor='blue')

        ax2 = ax1.twinx()
        ax2.step(full_data['Month'], full_data['Duration'], where='mid',
                 color='#f48fb1', linewidth=2)
        ax2.fill_between(full_data['Month'], full_data['Duration'],
                         step='mid', color='#f48fb1', alpha=0.3)
        ax2.set_ylabel('Average Duration (days)', color='pink')
        ax2.tick_params(axis='y', labelcolor='pink')

        for month, duration in zip(full_data['Month'], full_data['Duration']):
            if duration > 0:
                ax2.text(month, duration + 0.3, f"{duration:.1f} Days",
                         ha='center', va='bottom', fontsize=10, fontweight='bold', color='black')

        plt.title("Monthly Job Orders & Average Duration", fontsize=14)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)

        buf = io.BytesIO()
        fig.savefig(buf, format="jpeg", dpi=150, bbox_inches='tight')
        st.download_button("Download Chart", data=buf.getvalue(),
                           file_name="supply_chain_chart.jpeg", mime="image/jpeg")

    #### Add new entry form ####
    st.markdown("### ➕ Add New Supply Chain Entry")
    with st.form("add_supply"):
        job_order = st.text_input("Job Order")
        pr = st.text_input("PR Date (any format like 5/1/2025 or 01/05/2025)")
        po = st.text_input("PO Date (any format like 20/1/2025 or 01/20/2025)")
        submit = st.form_submit_button("Add Entry")
        if submit:
            try:
                new_row = pd.DataFrame([[job_order, pr, po]], columns=SUPPLYCHAIN_COLUMNS)
                updated_df = pd.concat([pd.read_csv(SUPPLYCHAIN_FILE), new_row], ignore_index=True)
                save_data(updated_df)
                st.success("Entry added!")
                st.rerun()
            except IOError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")
