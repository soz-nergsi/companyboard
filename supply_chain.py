import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
import requests
import json

SUPPLYCHAIN_FILE = 'supply_chain_data.csv'
SUPPLYCHAIN_COLUMNS = ['Job Order', 'PR', 'PO']

# Load credentials from Streamlit Secrets
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_USERNAME = st.secrets["GITHUB_USERNAME"]
GITHUB_REPO = st.secrets["GITHUB_REPO"]
GITHUB_BRANCH = st.secrets["GITHUB_BRANCH"]

def load_data():
    try:
        repo_api_url = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_REPO}/{GITHUB_BRANCH}/{SUPPLYCHAIN_FILE}"
        df = pd.read_csv(repo_api_url)
    except:
        df = pd.DataFrame(columns=SUPPLYCHAIN_COLUMNS)
    return df

def save_data_to_github(df, filename):
    repo_api_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{filename}"

    response = requests.get(repo_api_url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    sha = response.json()['sha'] if response.status_code == 200 else None

    csv_data = df.to_csv(index=False)
    encoded_data = base64.b64encode(csv_data.encode()).decode()

    payload = {
        "message": "Update supply_chain_data.csv via Streamlit",
        "content": encoded_data,
        "branch": GITHUB_BRANCH
    }
    if sha:
        payload["sha"] = sha

    put_response = requests.put(
        repo_api_url,
        headers={"Authorization": f"token {GITHUB_TOKEN}"},
        data=json.dumps(payload)
    )
    if put_response.status_code not in [200, 201]:
        st.error(f"❌ Failed to save data to GitHub: {put_response.json()}")

def render():
    st.subheader("🚛 Supply Chain Monthly Dashboard")

    df = load_data()
    st.dataframe(df, use_container_width=True)

    if not df.empty:
        # ✅ Fully parse after complete loading
        df['PR'] = pd.to_datetime(df['PR'], errors='coerce')
        df['PO'] = pd.to_datetime(df['PO'], errors='coerce')
        df = df.dropna(subset=['PR', 'PO'])
        df['Duration'] = (df['PO'] - df['PR']).dt.days

        total_job_orders = df['Job Order'].nunique()
        average_days = df['Duration'].mean()

        st.markdown(f"**Total Unique Job Orders:** {total_job_orders}")
        st.markdown(f"**Overall Average Duration:** {average_days:.1f} days")

    #### Add new entry form ####
    st.markdown("### ➕ Add New Supply Chain Entry")
    with st.form("add_supply"):
        job_order = st.text_input("Job Order")
        pr = st.text_input("PR Date (any format like 5/1/2025 or 01/05/2025)")
        po = st.text_input("PO Date (any format like 20/1/2025 or 01/20/2025)")
        submit = st.form_submit_button("Add Entry")
        if submit:
            new_row = pd.DataFrame([[job_order, pr, po]], columns=SUPPLYCHAIN_COLUMNS)
            updated_df = pd.concat([df, new_row], ignore_index=True)
            updated_df.to_csv(SUPPLYCHAIN_FILE, index=False)
            save_data_to_github(updated_df, SUPPLYCHAIN_FILE)
            st.success("✅ Entry added and saved to GitHub!")
            st.rerun()
