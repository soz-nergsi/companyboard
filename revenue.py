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

        below_200 = df[df['Amount'] <= 200].shape[0]
        above_200 = df[df['Amount'] > 200].shape[0]

        st.markdown("### 📊 Customer Rate Analysis")
        fig1, ax1 = plt.subplots(figsize=(3, 3))
        ax1.pie([below_200, above_200], labels=['≤ 200', '> 200'], autopct='%1.1f%%', startangle=90)
        ax1.set_title("Customer Distribution")
        st.pyplot(fig1)

        buf1 = io.BytesIO()
        fig1.savefig(buf1, format="jpeg", dpi=150, bbox_inches='tight')
        st.download_button("Download Customer Chart", data=buf1.getvalue(), file_name="customer_distribution.jpeg", mime="image/jpeg")

        min_rev = df['Amount'].min()
        impact = (min_rev / total) * 100

        st.markdown("### 📊 Revenue Impact")
        fig2, ax2 = plt.subplots(figsize=(3, 3))
        ax2.pie([min_rev, total - min_rev], labels=[f'Min Revenue ({impact:.1f}%)', 'Other'], autopct='%1.1f%%', startangle=90)
        ax2.set_title("Revenue Impact")
        st.pyplot(fig2)

        buf2 = io.BytesIO()
        fig2.savefig(buf2, format="jpeg", dpi=150, bbox_inches='tight')
        st.download_button("Download Revenue Impact Chart", data=buf2.getvalue(), file_name="revenue_impact.jpeg", mime="image/jpeg")

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
