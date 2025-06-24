import streamlit as st
import pandas as pd
import os

# File paths
REVENUE_FILE = 'finances revenue.csv'
SUPPLYCHAIN_FILE = 'supplyChain.csv'
SALES_FILE = 'Sales csv.csv'

# CSV structures
REVENUE_COLUMNS = ['DATE', 'Customer', 'Amount']
SUPPLYCHAIN_COLUMNS = ['Job Order', 'PR', 'PO']
SALES_COLUMNS = ['Job Order', 'Customer', 'Amount']

# Initial data
revenue_initial_data = [
    ['February', 'Gasin', '200$'],
    ['February', 'TCC', '900$'],
    ['February', 'Olympian Gym Center', '500$'],
    ['February', 'Hedi Jalil', '44$'],
    ['February', 'Asiacell', '35$']
]

supplychain_initial_data = [
    ['SPH91', '5/1/2025', '20/1/2025'],
    ['SPH77', '8/2/2025', '28/2/2025'],
    ['SPH66', '4/3/2025', '15/4/2025'],
    ['SPH17', '30/4/2025', '15/5/2025'],
    ['SPH11', '27/5/2025', '1/6/2025']
]

sales_initial_data = [
    ['s1', 'Seven Net', '100$'],
    ['s2', 'Azo Fashion', '200$'],
    ['s3', 'Asia Pay', '900$'],
    ['s4', 'eklam', '500$'],
    ['s5', 'FIG', '44$']
]

# Create files if not exist and insert initial data
def initialize_file(file_path, columns, data):
    if not os.path.exists(file_path):
        df = pd.DataFrame(data, columns=columns)
        df.to_csv(file_path, index=False)

initialize_file(REVENUE_FILE, REVENUE_COLUMNS, revenue_initial_data)
initialize_file(SUPPLYCHAIN_FILE, SUPPLYCHAIN_COLUMNS, supplychain_initial_data)
initialize_file(SALES_FILE, SALES_COLUMNS, sales_initial_data)

# Helper to clean amount fields
def clean_amount(val):
    try:
        return float(val.replace('$', '').strip())
    except:
        return 0.0

# Load data functions
@st.cache_data
def load_revenue():
    df = pd.read_csv(REVENUE_FILE)
    if not df.empty:
        df['Amount'] = df['Amount'].apply(clean_amount)
    return df

@st.cache_data
def load_supplychain():
    return pd.read_csv(SUPPLYCHAIN_FILE)

@st.cache_data
def load_sales():
    df = pd.read_csv(SALES_FILE)
    if not df.empty:
        df['Amount'] = df['Amount'].apply(clean_amount)
    return df

# Save data function
def save_data(file, df):
    df.to_csv(file, index=False)

# Streamlit page config
st.set_page_config(page_title="Company Monthly Dashboard", layout="wide")

# Initialize session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "Finances Revenue"

# Sidebar navigation
st.sidebar.title("📅 Monthly Dashboard")
if st.sidebar.button("💰 Finances Revenue"):
    st.session_state.page = "Finances Revenue"
if st.sidebar.button("🚛 Supply Chain"):
    st.session_state.page = "Supply Chain"
if st.sidebar.button("🛒 Sales"):
    st.session_state.page = "Sales"

# Main title
st.title("📊 Company Monthly Dashboard")

# Finances Revenue Page
if st.session_state.page == "Finances Revenue":
    st.subheader("💰 Finances Revenue Overview")
    revenue_df = load_revenue()
    st.dataframe(revenue_df, use_container_width=True)

    if not revenue_df.empty:
        st.metric("Total Revenue", f"${revenue_df['Amount'].sum():,.2f}")

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
            st.experimental_rerun()

# Supply Chain Page
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
            st.experimental_rerun()

# Sales Page
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
            st.experimental_rerun()
