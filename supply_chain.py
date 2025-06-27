import streamlit as st
import pandas as pd
import os
import datetime
import base64
import requests

CSV_FILE = "supply_chain_data.csv"
COLUMNS = ["Job Order", "PR", "PO"]

# Load data
def load_data():
    if not os.path.exists(CSV_FILE):
        pd.DataFrame(columns=COLUMNS).to_csv(CSV_FILE, index=False)
    return pd.read_csv(CSV_FILE)

# Save data locally
def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# Upload to GitHub if token and repo info are present
def upload_to_github():
    try:
        token = st.secrets["GITHUB_TOKEN"]
        username = st.secrets["GITHUB_USERNAME"]
        repo = st.secrets["GITHUB_REPO"]
        branch = st.secrets["GITHUB_BRANCH"]
    except KeyError:
        return  # GitHub settings not configured

    api_url = f"https://api.github.com/repos/{username}/{repo}/contents/{CSV_FILE}"
    headers = {"Authorization": f"token {token}"}

    # Read file content and encode
    with open(CSV_FILE, "rb") as f:
        content = f.read()
        encoded = base64.b64encode(content).decode()

    # Get current SHA
    response = requests.get(api_url, headers=headers)
    sha = response.json().get("sha")

    commit_message = "Auto update supply chain data"
    payload = {
        "message": commit_message,
        "content": encoded,
        "branch": branch,
        "sha": sha,
    }
    requests.put(api_url, headers=headers, json=payload)

def render():
    st.subheader("🚛 Supply Chain Monthly Dashboard")

    df = load_data()
    st.dataframe(df, use_container_width=True)

    # Parse dates
    df['PR'] = pd.to_datetime(df['PR'], errors='coerce', dayfirst=True)
    df['PO'] = pd.to_datetime(df['PO'], errors='coerce', dayfirst=True)
    df['Duration'] = (df['PO'] - df['PR']).dt.days
    df['Month'] = df['PR'].dt.strftime('%B')

    # Calculate metrics
    monthly_summary = df.groupby('Month').agg({
        'Job Order': 'count',
        'Duration': 'mean'
    }).rename(columns={'Job Order': 'Job Orders', 'Duration': 'Avg Duration'}).reset_index()

    # Reorder months
    month_order = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    monthly_summary['Month'] = pd.Categorical(monthly_summary['Month'], categories=month_order, ordered=True)
    monthly_summary = monthly_summary.sort_values('Month')

    # Plot
    import matplotlib.pyplot as plt

    fig, ax1 = plt.subplots(figsize=(10, 5))

    ax2 = ax1.twinx()
    ax1.bar(monthly_summary['Month'], monthly_summary['Job Orders'], color='skyblue', label='Job Orders')
    ax2.plot(monthly_summary['Month'], monthly_summary['Avg Duration'], color='orange', marker='o', label='Avg Duration (days)')

    ax1.set_ylabel("Job Orders", color='blue')
    ax2.set_ylabel("Avg Duration (days)", color='orange')
    ax1.set_xlabel("Month")
    fig.suptitle("📈 Job Orders and Average Duration")

    # Add data labels
    for i, v in enumerate(monthly_summary['Job Orders']):
        ax1.text(i, v + 0.1, str(v), ha='center', color='blue')

    for i, v in enumerate(monthly_summary['Avg Duration']):
        ax2.text(i, v + 1, f"{v:.1f}", ha='center', color='orange')

    st.pyplot(fig)

    # Add new entry
    st.markdown("### ➕ Add New Supply Chain Entry")
    with st.form("add_supply_chain_entry"):
        job_order = st.text_input("Job Order")
        pr = st.date_input("PR Date")
        po = st.date_input("PO Date")
        submit = st.form_submit_button("Submit")

        if submit:
            new_row = pd.DataFrame([[job_order, pr.strftime("%d/%m/%Y"), po.strftime("%d/%m/%Y")]], columns=COLUMNS)
            updated_df = pd.concat([df.dropna(subset=['PR', 'PO']), new_row], ignore_index=True)
            save_data(updated_df)
            upload_to_github()
            st.success("✅ Entry added and CSV updated.")
            st.rerun()
