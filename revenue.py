import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
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

        # Split into groups
        below_200_df = df[df['Amount'] <= 200]
        above_200_df = df[df['Amount'] > 200]

        # First Pie Chart — Customer Rate
        st.markdown("### 📊 Customer Rate")
        below_count = below_200_df.shape[0]
        above_count = above_200_df.shape[0]

        fig1, ax1 = plt.subplots(figsize=(3, 3))
        ax1.pie(
            [below_count, above_count],
            labels=["≤ $200", "> $200"],
            autopct='%1.1f%%',
            startangle=90
        )
        ax1.set_title("Customer Rate Analysis")
        st.pyplot(fig1)

        buf1 = io.BytesIO()
        fig1.savefig(buf1, format="jpeg", dpi=150, bbox_inches='tight')
        st.download_button(
            "Download Customer Rate Chart",
            data=buf1.getvalue(),
            file_name="customer_rate.jpeg",
            mime="image/jpeg"
        )

        # Second Pie Chart — Revenue Percentage Impact
        st.markdown("### 📊 Revenue Percentage Impact")
        below_revenue = below_200_df['Amount'].sum()
        above_revenue = above_200_df['Amount'].sum()

        below_pct = (below_revenue / total) * 100
        above_pct = (above_revenue / total) * 100

        fig2, ax2 = plt.subplots(figsize=(3, 3))
        ax2.pie(
            [below_revenue, above_revenue],
            labels=[
                f"≤ $200 — {below_pct:.1f}%",
                f"> $200 — {above_pct:.1f}%"
            ],
            autopct='%1.1f%%',
            startangle=90
        )
        ax2.set_title("Revenue Percentage Impact")
        st.pyplot(fig2)

        buf2 = io.BytesIO()
        fig2.savefig(buf2, format="jpeg", dpi=150, bbox_inches='tight')
        st.download_button(
            "Download Revenue Impact Chart",
            data=buf2.getvalue(),
            file_name="revenue_percentage_impact.jpeg",
            mime="image/jpeg"
        )

    # Add new entry form
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
