import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import io

SUPPLYCHAIN_FILE = 'supply_chain_data.csv'
SUPPLYCHAIN_COLUMNS = ['Job Order', 'PR', 'PO']

# Initialize file if doesn't exist
def initialize_file():
    if not os.path.exists(SUPPLYCHAIN_FILE):
        pd.DataFrame(columns=SUPPLYCHAIN_COLUMNS).to_csv(SUPPLYCHAIN_FILE, index=False)

initialize_file()

# Load data
def load_data():
    return pd.read_csv(SUPPLYCHAIN_FILE)

# Save data
def save_data(df):
    df.to_csv(SUPPLYCHAIN_FILE, index=False)

# Main render function
def render():
    st.subheader("🚛 Supply Chain Overview")
    df = load_data()
    st.dataframe(df, use_container_width=True)

    # Only process if data exists
    if not df.empty:
        # Convert to datetime
        df['PR'] = pd.to_datetime(df['PR'], format='%d/%m/%Y')
        df['PO'] = pd.to_datetime(df['PO'], format='%d/%m/%Y')

        # Calculate duration
        df['Duration'] = (df['PO'] - df['PR']).dt.days

        # Extract month
        df['Month'] = df['PR'].dt.strftime('%B')

        # Group data by month
        month_group = df.groupby('Month').agg({
            'Job Order': 'count',
            'Duration': 'mean'
        }).reset_index()

        # Build full months list (January to December)
        months_full = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']

        # Prepare full data with missing months filled
        full_data = pd.DataFrame({'Month': months_full})
        full_data = full_data.merge(month_group, on='Month', how='left').fillna(0)
        full_data['Job Order'] = full_data['Job Order'].astype(int)

        st.markdown(f"**Total Job Orders:** {df.shape[0]}")
        st.markdown(f"**Average Duration (days):** {df['Duration'].mean():.1f}")

        # Plot
        fig, ax1 = plt.subplots(figsize=(8, 5))

        # Bar plot for Job Orders count
        bars = ax1.bar(full_data['Month'], full_data['Job Order'], color='#90caf9')

        # Add labels inside bars
        for bar, count in zip(bars, full_data['Job Order']):
            if count > 0:
                ax1.text(bar.get_x() + bar.get_width() / 2, count + 0.1, f"{count} Job Orders",
                         ha='center', va='bottom', fontsize=9)

        ax1.set_xlabel('Month')
        ax1.set_ylabel('Number of Job Orders', color='blue')
        ax1.tick_params(axis='y', labelcolor='blue')

        # Secondary axis: Stepped area for duration
        ax2 = ax1.twinx()
        ax2.step(full_data['Month'], full_data['Duration'], where='mid', color='#f48fb1', linewidth=2)
        ax2.fill_between(full_data['Month'], full_data['Duration'], step='mid', color='#f48fb1', alpha=0.3)
        ax2.set_ylabel('Average Duration (days)', color='pink')
        ax2.tick_params(axis='y', labelcolor='pink')

        # Add labels for stepped area (only for months with data)
        for month, duration in zip(full_data['Month'], full_data['Duration']):
            if duration > 0:
                ax2.text(month, duration + 0.1, f"{duration:.1f} Days", ha='center', va='bottom', fontsize=9)

        plt.title("Monthly Job Orders & Average Duration")
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)

        # Downloadable chart
        buf = io.BytesIO()
        fig.savefig(buf, format="jpeg", dpi=150, bbox_inches='tight')
        st.download_button("Download Supply Chain Chart", data=buf.getvalue(),
                           file_name="supply_chain_chart.jpeg", mime="image/jpeg")

    #### Add new entry form ####
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
