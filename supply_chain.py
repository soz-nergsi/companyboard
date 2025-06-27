import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import streamlit as st
from github import Github
from datetime import datetime

# GitHub config from secrets
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_REPO = st.secrets["GITHUB_REPO"]
GITHUB_FILE = st.secrets["GITHUB_FILE"]
GITHUB_BRANCH = st.secrets["GITHUB_BRANCH"]

# Load CSV from GitHub
def load_data():
    g = Github(GITHUB_TOKEN)
    repo = g.get_user().get_repo(GITHUB_REPO)
    file_content = repo.get_contents(GITHUB_FILE, ref=GITHUB_BRANCH)
    return pd.read_csv(BytesIO(file_content.decoded_content))

# Save updated CSV back to GitHub
def save_data(df):
    g = Github(GITHUB_TOKEN)
    repo = g.get_user().get_repo(GITHUB_REPO)
    file = repo.get_contents(GITHUB_FILE, ref=GITHUB_BRANCH)
    csv_data = df.to_csv(index=False).encode()
    repo.update_file(file.path, "Update supply chain data", csv_data, file.sha, branch=GITHUB_BRANCH)

# Main dashboard renderer
def render():
    st.subheader("🚛 Supply Chain Monthly Dashboard")

    df = load_data()
    df['PR'] = pd.to_datetime(df['PR'])
    df['PO'] = pd.to_datetime(df['PO'])
    df['Duration'] = (df['PO'] - df['PR']).dt.days
    df['Month'] = df['PR'].dt.strftime('%B')

    monthly = df.groupby('Month').agg(
        JobOrders=('Job Order', 'count'),
        AvgDuration=('Duration', 'mean')
    ).reset_index()
    monthly['MonthNum'] = pd.to_datetime(monthly['Month'], format='%B').dt.month
    monthly = monthly.sort_values('MonthNum')

    # 📊 Plotting
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.bar(monthly['Month'], monthly['JobOrders'], label='Job Orders')
    for idx, row in monthly.iterrows():
        ax1.text(row['Month'], row['JobOrders'], f"{int(row['JobOrders'])}", ha='center', va='bottom')

    ax2 = ax1.twinx()
    ax2.step(monthly['Month'], monthly['AvgDuration'], where='mid', color='orange', label='Avg Duration')
    for idx, row in monthly.iterrows():
        ax2.text(row['Month'], row['AvgDuration'], f"{int(row['AvgDuration'])}d", ha='center', va='bottom', color='orange')

    ax1.set_ylabel('Job Orders')
    ax2.set_ylabel('Avg Duration (days)')
    fig.tight_layout()
    st.pyplot(fig)

    # 📋 Raw data table
    st.markdown("### 📋 Supply Chain Table")
    st.dataframe(df, use_container_width=True)

    # ➕ Add new data
    st.markdown("### ➕ Add Job Order")
    with st.form("add_order"):
        job_order = st.text_input("Job Order")
        pr_date = st.date_input("PR Date")
        po_date = st.date_input("PO Date")
        submitted = st.form_submit_button("Submit")
        if submitted:
            new_row = {
                "Job Order": job_order,
                "PR": pd.to_datetime(pr_date),
                "PO": pd.to_datetime(po_date),
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df['Duration'] = (df['PO'] - df['PR']).dt.days
            df['Month'] = df['PR'].dt.strftime('%B')
            save_data(df)
            st.success("✅ Job order added successfully!")
            st.rerun()
