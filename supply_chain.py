import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

CSV_FILE = "supply_chain_data.csv"

def load_data():
    return pd.read_csv(CSV_FILE)

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

def render():
    st.subheader("🚛 Supply Chain Monthly Dashboard")

    df = load_data()
    st.dataframe(df, use_container_width=True)

    if not df.empty:
        df['PR'] = pd.to_datetime(df['PR'], dayfirst=True, errors='coerce')
        df['PO'] = pd.to_datetime(df['PO'], dayfirst=True, errors='coerce')
        df['Month'] = df['PR'].dt.strftime('%B')
        df['Duration'] = (df['PO'] - df['PR']).dt.days

        month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
        df['Month'] = pd.Categorical(df['Month'], categories=month_order, ordered=True)

        monthly_stats = df.groupby('Month').agg(
            Job_Count=('Job Order', 'count'),
            Avg_Duration=('Duration', 'mean')
        ).reset_index().dropna()

        fig, ax1 = plt.subplots(figsize=(10, 5))
        bars = ax1.bar(monthly_stats['Month'], monthly_stats['Job_Count'], label='Job Orders', color='gray')
        ax1.set_ylabel("Job Orders", color="gray")
        ax1.tick_params(axis='y', labelcolor="gray")

        # Job Order labels
        for bar in bars:
            height = bar.get_height()
            ax1.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width() / 2, height),
                         xytext=(0, 3), textcoords="offset points", ha='center', fontsize=9)

        ax2 = ax1.twinx()
        ax2.step(monthly_stats['Month'], monthly_stats['Avg_Duration'], label='Avg Duration', color='green', where='mid')
        ax2.set_ylabel("Avg Duration (Days)", color="green")
        ax2.tick_params(axis='y', labelcolor="green")

        # Avg Duration labels
        for i, avg in enumerate(monthly_stats['Avg_Duration']):
            ax2.annotate(f'{avg:.1f}', xy=(i, avg), xytext=(0, -15),
                         textcoords="offset points", ha='center', color='green', fontsize=9)

        st.pyplot(fig)

    # Add new entry
    st.markdown("### ➕ Add New Supply Chain Entry")
    with st.form("add_supply_chain"):
        job_order = st.text_input("Job Order")
        pr = st.text_input("PR Date (dd/mm/yyyy)")
        po = st.text_input("PO Date (dd/mm/yyyy)")
        submit = st.form_submit_button("Add Entry")
        if submit:
            try:
                new_row = pd.DataFrame([[job_order, pr, po]], columns=["Job Order", "PR", "PO"])
                df = pd.concat([df, new_row], ignore_index=True)
                save_data(df)
                st.success("New supply chain entry added!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
