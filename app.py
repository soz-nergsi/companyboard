import streamlit as st
import revenue
import supply_chain
import sales

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

st.title("📊 Company Monthly Dashboard")

# Call the corresponding module
if st.session_state.page == "Finances Revenue":
    revenue.render()
elif st.session_state.page == "Supply Chain":
    supply_chain.render()
elif st.session_state.page == "Sales":
    sales.render()
