import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import io

# File paths
REVENUE_FILE = 'revenue_data.csv'
SUPPLYCHAIN_FILE = 'supply_chain_data.csv'
SALES_FILE = 'sales_data.csv'

# CSV structures
REVENUE_COLUMNS = ['DATE', 'Customer', 'Amount']
SUPPLYCHAIN_COLUMNS = ['Job Order', 'PR', 'PO']
SALES_COLUMNS = ['Job Order', 'Customer', 'Amount']

# Create empty files if not exist
def initialize_file(file_path, columns):
    if not os.path.exists(file_path):
        pd.DataFrame(columns=columns).to_csv(file_path, index=False)

initialize_file(REVENUE_FILE, REVENUE_COLUMNS)
initialize_file(SUPPLYCHAIN_FILE, SUPPLYCHAIN_COLUMNS)
initialize_file(SALES_FILE, SALES_COLUMNS)

def clean_amount(val):
    try:
        return float(val.replace('$', '').strip())
    except:
        return 0.0

def load_revenue():
    df = pd.read_csv(REVENUE_FILE)
    if not df.empty:
        df['Amount'] = df['Amount'].apply(clean_amount)
    return df

def load_supplychain():
    return pd.read_csv(SUPPLYCHAIN_FILE)

def load_sales():
    df = pd.read_csv(SALES_FILE)
    if not df.empty:
        df['Amount'] = df['Amount'].apply(clean_amount)
    return df

def save_data(file, df):
    df.to_csv(file, index=False)

st.set_page_config(page_title="Company Monthly Dashboard", layout="wide")

if "page" not in st.session_state:
    st.session_state.page = "Finances Revenue"

st.sidebar.title("📅 Monthly Dashboard")
if st.sidebar.button("💰 Finances Revenue"):
    st.session_state.page = "Finances Revenue"
if st.sidebar.button("🚛 Supply Chain"):
    st.session_state.page = "Supply Chain"
if st.sidebar.button("🛒 Sales"):
    st.session_state.page = "Sales"

st.title("📊 Company Monthly Dashboard")

if st.session_state.page == "Finances Revenue":
    st.subheader("💰 Finances Revenue Overview")
    revenue_df = load_revenue()
    st.dataframe(revenue_df, use_container_width=True)

    if not revenue_df.empty:
        total_revenue = revenue_df['Amount'].sum()
        st.metric("Total Revenue", f"${total_revenue:,.2f}")

        below_200 = revenue_df[revenue_df['Amount'] <= 200].shape[0]
        above_200 = revenue_df[revenue_df['Amount'] > 200].shape[0]

        st.markdown("### 📊 Customer Rate Analysis")
        fig1, ax1 = plt.subplots(figsize=(3, 3))
        ax1.pie([below_200, above_200],
                labels=['≤ 200', '> 200'],
                autopct='%1.1f%%',
                startangle=90)
        ax1.set_title("Customer Distribution")
        st.pyplot(fig1)

        buf1 = io.BytesIO()
        fig1.savefig(buf1, format="jpeg", dpi=150, bbox_inches='tight')
        st.download_button("Download Customer Chart", data=buf1.getvalue(),
                           file_name="customer_distribution.jpeg", mime="image/jpeg")

        st.write(f"Total Customers: {below_200 + above_200}")
        st.write(f"Customers ≤ 200: {below_200}")
        st.write(f"Customers > 200: {above_200}")

        min_revenue = revenue_df['Amount'].min()
        impact_value = (min_revenue / total_revenue) * 100

        st.markdown("### 📊 Revenue Impact")
        fig2, ax2 = plt.subplots(figsize=(3, 3))
        ax2.pie([min_revenue, total_revenue - min_revenue],
                labels=[f'Minimum Revenue ({impact_value:.1f}%)', 'Other'],
                autopct='%1.1f%%',
                startangle=90)
        ax2.set_title("Revenue Impact")
        st.pyplot(fig2)

        buf2 = io.BytesIO()
        fig2.savefig(buf2, format="jpeg", dpi=150, bbox_inches='tight')
        st.download_button("Download Revenue Impact Chart", data=buf2.getvalue(),
                           file_name="revenue_impact.jpeg", mime="image/jpeg")

    st.markdown("### ➕ Add New Revenue Entry")
    with st.form("add_revenue"):
        date = st.text_input("Date (e.g. February)", value="February")
        customer = st.text_input("Customer")
        amount = st.number_input("Amount ($)", min_value=0.0, step=0.01)
        submit = st.form_submit_button("Add Revenue")
        if submit:
            new_row = pd.DataFrame([[date, customer, f"{amount:.2f}$"]], columns=REVENUE_COLUMNS)
            updated_df = pd.concat([pd.read_csv(REVENUE_FILE), new_row], ignore_index=True)
            save_data(REVENUE_FILE, updated_df)
            st.success("Revenue entry added!")
            st.rerun()

elif st.session_state.page == "Supply Chain":
    st.subheader("🚛 Supply Chain Overview")
    supply_df = load_supplychain()
    st.dataframe(supply_df, use_container_width=True)

    if not supply_df.empty:
        st.metric("Total Orders", len(supply_df))

    st.markdown("### ➕ Add New Supply Chain Entry")
    with st.form("add_supply"):
        job_order = st.text_input("Job Order")
        pr = st.text_input("PR Date (e.g. 5/1/2025)")
        po = st.text_input("PO Date (e.g. 20/1/2025)")
        submit = st.form_submit_button("Add Supply Entry")
        if submit:
            new_row = pd.DataFrame([[job_order, pr, po]], columns=SUPPLYCHAIN_COLUMNS)
            updated_df = pd.concat([pd.read_csv(SUPPLYCHAIN_FILE), new_row], ignore_index=True)
            save_data(SUPPLYCHAIN_FILE, updated_df)
            st.success("Supply chain entry added!")
            st.rerun()

elif st.session_state.page == "Sales":
    st.subheader("🛒 Sales Overview")
    sales_df = load_sales()
    st.dataframe(sales_df, use_container_width=True)

    if not sales_df.empty:
        st.metric("Total Sales Amount", f"${sales_df['Amount'].sum():,.2f}")

    st.markdown("### ➕ Add New Sales Entry")
    with st.form("add_sales"):
        job_order = st.text_input("Job Order")
        customer = st.text_input("Customer")
        amount = st.number_input("Amount ($)", min_value=0.0, step=0.01)
        submit = st.form_submit_button("Add Sales Entry")
        if submit:
            new_row = pd.DataFrame([[job_order, customer, f"{amount:.2f}$"]], columns=SALES_COLUMNS)
            updated_df = pd.concat([pd.read_csv(SALES_FILE), new_row], ignore_index=True)
            save_data(SALES_FILE, updated_df)
            st.success("Sales entry added!")
            st.rerun()
