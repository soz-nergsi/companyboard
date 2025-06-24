import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Company Monthly Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "Finances Revenue"

# Sidebar
st.sidebar.title("📅 Monthly Dashboard")

# Button-like navigation
if st.sidebar.button("💰 Finances Revenue"):
    st.session_state.page = "Finances Revenue"
if st.sidebar.button("🚛 Supply Chain"):
    st.session_state.page = "Supply Chain"
if st.sidebar.button("🛒 Sales"):
    st.session_state.page = "Sales"

# Main Title
st.title("📊 Company Monthly Dashboard")

# Display selected page
if st.session_state.page == "Finances Revenue":
    st.subheader("💰 Finances Revenue Overview")
    st.info("Here you can display revenue data and charts.")

elif st.session_state.page == "Supply Chain":
    st.subheader("🚛 Supply Chain Overview")
    st.info("Here you can display supply chain data and metrics.")

elif st.session_state.page == "Sales":
    st.subheader("🛒 Sales Overview")
    st.info("Here you can display sales data and summaries.")
