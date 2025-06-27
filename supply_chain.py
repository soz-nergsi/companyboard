import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from io import BytesIO

SUPPLY_CHAIN_FILE = "supplychain_data.csv"

def load_data():
    df = pd.read_csv(SUPPLY_CHAIN_FILE)
    df["PR"] = pd.to_datetime(df["PR"], format="%d/%m/%Y")
    df["PO"] = pd.to_datetime(df["PO"], format="%d/%m/%Y")
    df["Duration"] = (df["PO"] - df["PR"]).dt.days
    df["Month"] = df["PR"].dt.strftime("%B")
    return df

def render():
    st.subheader("🚛 Supply Chain Monthly Dashboard")
    df = load_data()
    st.dataframe(df, use_container_width=True)

    monthly = df.groupby("Month").agg(
        JobOrders=("Job Order", "count"),
        AvgDuration=("Duration", "mean")
    ).reindex([
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]).dropna()

    # Plot
    fig, ax1 = plt.subplots(figsize=(10, 6))
    months = monthly.index
    orders = monthly["JobOrders"]
    durations = monthly["AvgDuration"]

    # Bar for job orders
    bars = ax1.bar(months, orders, color='gold')
    ax1.set_ylabel("Total Requests", color='black')
    ax1.tick_params(axis='y', labelcolor='black')
    ax1.set_ylim(0, max(orders) + 10)

    for bar in bars:
        height = bar.get_height()
        ax1.annotate(f"{int(height)}", xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=10)

    # Stepped line for duration
    ax2 = ax1.twinx()
    ax2.plot(months, durations, color='magenta', linewidth=2, drawstyle='steps-post')
    ax2.set_ylabel("Avg PR-PO Duration (Days)", color='magenta')
    ax2.tick_params(axis='y', labelcolor='magenta')
    ax2.set_ylim(0, max(durations) + 2)

    for i, val in enumerate(durations):
        ax2.annotate(f"{val:.1f} Days", (i, val), textcoords="offset points",
                     xytext=(0, 8), ha='center', color='magenta', fontsize=9)

    plt.title("PR Rate & AVG Cycle Duration")
    fig.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    st.image(buffer)
