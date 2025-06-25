import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import io

REVENUE_FILE = 'revenue_data.csv'
REVENUE_COLUMNS = ['DATE', 'Customer', 'Amount']

def initialize_file():
    if not os.path.exists(REVENUE_FILE):
        pd.DataFrame(columns=REVENUE_COLUMNS).to_csv(REVENUE_FILE, index=False)

initialize_file()

def clean_amount(val):
    try:
        return float(val.replace('$', '').strip())
    except:
        return 0.0

def load_data():
    df = pd.read_csv(REVENUE_FILE)
    if not df.empty:
        df['Amount'] = df['Amount'].apply(clean_amount)
    return df

def save_data(df):
    df.to_csv(REVENUE_FILE, index=False)

def render():
    st.subheader("💰 Finances Revenue Overview")
    df = load_data()
    st.dataframe(df, use_container_width=True)

    if not df.empty:
        total = df['Amount'].sum()
        st.metric("Total Revenue", f"${total:,.2f}")

        # Split groups
        below_df = df[df['Amount'] <= 200]
        above_df = df[df['Amount'] > 200]

        below_count = below_df.shape[0]
        above_count = above_df.shape[0]
        total_count = below_count + above_count

        # First Chart: Customer Rate Analysis
        st.markdown("### 📊 Customer Rate Analysis")

        sizes = [below_count, above_count]
        labels = ["≤ $200", "> $200"]
        colors = ['yellow', 'orange']

        fig1, ax1 = plt.subplots(figsize=(4, 4))
        wedges, texts, autotexts = ax1.pie(
            sizes,
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'color': "black", 'fontsize': 10}
        )
        # External labels for counts
        for i, wedge in enumerate(wedges):
            angle = (wedge.theta2 + wedge.theta1) / 2
            x = np.cos(np.deg2rad(angle))
            y = np.sin(np.deg2rad(angle))
            ha = 'left' if x > 0 else 'right'
            ax1.text(1.1 * x, 1.1 * y, f"{sizes[i]} customers", ha=ha, va='center', fontsize=9)

        ax1.set_title("Customer Rate Analysis")
        ax1.legend(wedges, labels, title="Legend", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        st.pyplot(fig1)

        buf1 = io.BytesIO()
        fig1.savefig(buf1, format="jpeg", dpi=150, bbox_inches='tight')
        st.download_button("Download Customer Rate Chart", data=buf1.getvalue(),
                           file_name="customer_rate.jpeg", mime="image/jpeg")

        # Second Chart: Revenue Percentage Impact
        st.markdown("### 📊 Revenue Percentage Impact")

        below_revenue = below_df['Amount'].sum()
        above_revenue = above_df['Amount'].sum()

        below_pct = (below_revenue / total) * 100
        above_pct = (above_revenue / total) * 100

        sizes_rev = [below_revenue, above_revenue]

        fig2, ax2 = plt.subplots(figsize=(4, 4))
        wedges2, texts2, autotexts2 = ax2.pie(
            sizes_rev,
            labels=[f"≤ $200", "> $200"],
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'color': "black", 'fontsize': 10}
        )
        # External labels for revenue amounts
        for i, wedge in enumerate(wedges2):
            angle = (wedge.theta2 + wedge.theta1) / 2
            x = np.cos(np.deg2rad(angle))
            y = np.sin(np.deg2rad(angle))
            ha = 'left' if x > 0 else 'right'
            ax2.text(1.1 * x, 1.1 * y, f"${sizes_rev[i]:,.0f}", ha=ha, va='center', fontsize=9)

        ax2.set_title("Revenue Percentage Impact")
        ax2.legend(wedges2, labels, title="Legend", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        st.pyplot(fig2)

        buf2 = io.BytesIO()
        fig2.savefig(buf2, format="jpeg", dpi=150, bbox_inches='tight')
        st.download_button("Download Revenue Impact Chart", data=buf2.getvalue(),
                           file_name="revenue_impact.jpeg", mime="image/jpeg")

    # Add data form
    st.markdown("### ➕ Add New Revenue Entry")
    with st.form("add_revenue"):
        date = st.text_input("Date (e.g. February)", value="February")
        customer = st.text_input("Customer")
        amount = st.number_input("Amount ($)", min_value=0.0, step=0.01)
        submit = st.form_submit_button("Add Revenue")
        if submit:
            new_row = pd.DataFrame([[date, customer, f"{amount:.2f}$"]], columns=REVENUE_COLUMNS)
            updated_df = pd.concat([pd.read_csv(REVENUE_FILE), new_row], ignore_index=True)
            save_data(updated_df)
            st.success("Revenue entry added!")
            st.rerun()
