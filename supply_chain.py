import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from datetime import datetime
from github import Github, GithubException
import matplotlib.pyplot as plt

# GitHub secrets
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_USERNAME = st.secrets["GITHUB_USERNAME"]
GITHUB_REPO = st.secrets["GITHUB_REPO"]
GITHUB_BRANCH = st.secrets["GITHUB_BRANCH"]
CSV_PATH = st.secrets["CSV_PATH"]

# Authenticate with GitHub
g = Github(GITHUB_TOKEN)
repo = g.get_user().get_repo(GITHUB_REPO)

def load_data():
    try:
        contents = repo.get_contents(CSV_PATH, ref=GITHUB_BRANCH)
        df = pd.read_csv(BytesIO(contents.decoded_content))
        return df
    except GithubException as e:
        st.error("Failed to load CSV from GitHub.")
        return pd.DataFrame(columns=["Job Order", "PR", "PO"])

def save_data(df):
    try:
        contents = repo.get_contents(CSV_PATH, ref=GITHUB_BRANCH)
        repo.update_file(
            path=CSV_PATH,
            message="Update supply chain data",
            content=df.to_csv(index=False),
            sha=contents.sha,
            branch=GITHUB_BRANCH
        )
    except GithubException as e:
        st.error("Failed to update CSV on GitHub.")

def render():
    st.subheader("🚛 Supply Chain Monthly Dashboard")

    df = load_data()
    st.dataframe(df, use_container_width=True)

    #### Clean and prepare data ####
    if not df.empty:
        # Convert PR and PO to datetime
        df["PR"] = pd.to_datetime(df["PR"], errors="coerce", dayfirst=False)
        df["PO"] = pd.to_datetime(df["PO"], errors="coerce", dayfirst=False)

        # Drop rows with invalid dates
        df = df.dropna(subset=["PR", "PO"])

        # Calculate Duration and Month
        df["Duration"] = (df["PO"] - df["PR"]).dt.days
        df["Month"] = df["PR"].dt.strftime("%B")

        # Aggregate
        summary = df.groupby("Month").agg({
            "Job Order": "count",
            "Duration": "mean"
        }).rename(columns={
            "Job Order": "Total Job Orders",
            "Duration": "Average Duration (days)"
        }).reset_index()

        #### Plotting ####
        fig, ax1 = plt.subplots(figsize=(8, 4))

        ax2 = ax1.twinx()
        ax1.bar(summary["Month"], summary["Total Job Orders"], color="lightblue", label="Job Orders")
        ax2.plot(summary["Month"], summary["Average Duration (days)"], color="orange", marker="o", label="Avg Duration")

        ax1.set_ylabel("Job Orders")
        ax2.set_ylabel("Avg Duration (days)")
        ax1.set_title("Monthly Job Orders and Average Duration")

        fig.tight_layout()
        st.pyplot(fig)

    #### Add new data ####
    st.markdown("### ➕ Add New Job Order")
    with st.form("add_job_order_form"):
        job_order = st.text_input("Job Order (e.g., SPH101)")
        pr = st.date_input("PR Date")
        po = st.date_input("PO Date")
        submitted = st.form_submit_button("Add Job Order")

        if submitted:
            if po < pr:
                st.error("PO Date must be after PR Date.")
            else:
                new_entry = pd.DataFrame([{
                    "Job Order": job_order,
                    "PR": pr.strftime("%d/%m/%Y"),
                    "PO": po.strftime("%d/%m/%Y")
                }])
                df = pd.concat([df, new_entry], ignore_index=True)
                save_data(df)
                st.success("Job order added successfully!")
                st.rerun()
