import streamlit as st
import pandas as pd
import os
import datetime
import matplotlib.pyplot as plt
from io import BytesIO
from github import Github

CSV_FILE = "supply_chain_data.csv"
COLUMNS = ["Job Order", "PR", "PO"]

def initialize_file():
    if not os.path.exists(CSV_FILE):
        pd.DataFrame(columns=COLUMNS).to_csv(CSV_FILE, index=False)

def load_data():
    df = pd.read_csv(CSV_FILE)
    df.dropna(inplace=True)
    df["PR"] = pd.to_datetime(df["PR"], dayfirst=True)
    df["PO"] = pd.to_datetime(df["PO"], dayfirst=True)
    df["Duration"] = (df["PO"] - df["PR"]).dt.days
    df["Month"] = df["PR"].dt.strftime('%B')
    return df

def save_data(df):
    df.to_csv(CSV_FILE, index=False)
    if "GITHUB_TOKEN" in st.secrets:
        push_to_github()

def push_to_github():
    token = st.secrets["GITHUB_TOKEN"]
    repo_name = st.secrets["GITHUB_REPO"]
    path = st.secrets["GITHUB_FILE"]
    branch = st.secrets.get("GITHUB_BRANCH", "main")
    
    g = Github(token)
    repo = g.get_repo(repo_name)
    with open(CSV_FILE, "r") as file:
        content = file.read()

    try:
        contents = repo.get_contents(path, ref=branch)
        repo.update_file(contents.path, "Update supply chain data", content, contents.sha, branch=branch)
    except Exception:
        repo.create_file(path, "Create supply chain data", content, branch=branch)

def plot_chart(df):
    summary = df.groupby("Month").agg(
        Job_Orders=("Job Order", "count"),
        Avg_Duration=("Duration", "mean")
    ).reset_index()

    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax2 = ax1.twinx()

    bars = ax1.bar(summary["Month"], summary["Job_Orders"], label="Job Orders", alpha=0.6)
    line = ax2.step(summary["Month"], summary["Avg_Duration"], where='mid', label="Avg Duration (days)", color='orange')
    
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2.0, height, f'{int(height)}', ha='center', va='bottom')

    for i, val in enumerate(summary["Avg_Duration"]):
        ax2.text(i, val + 0.5, f"{val:.1f}d", ha='center', va='bottom', fontsize=9, color='orange')

    ax1.set_ylabel("Job Orders")
    ax2.set_ylabel("Avg Duration (days)")
    ax1.set_title("Monthly Job Orders and Avg. Duration")
    fig.tight_layout()
    st.pyplot(fig)

def render():
    st.subheader("🚛 Supply Chain Monthly Dashboard")

    initialize_file()
    df = load_data()
    st.dataframe(df, use_container_width=True)

    if not df.empty:
        plot_chart(df)

    st.markdown("### ➕ Add New Supply Chain Entry")
    with st.form("add_supply_chain"):
        job_order = st.text_input("Job Order")
        pr = st.date_input("PR Date")
        po = st.date_input("PO Date")
        submit = st.form_submit_button("Add Entry")
        if submit:
            try:
                new_row = pd.DataFrame([[job_order, pr.strftime('%d/%m/%Y'), po.strftime('%d/%m/%Y')]], columns=COLUMNS)
                updated_df = pd.concat([pd.read_csv(CSV_FILE), new_row], ignore_index=True)
                save_data(updated_df)
                st.success("Supply chain entry added!")
                st.rerun()
            except Exception as e:
                st.error(f"Error adding entry: {e}")
