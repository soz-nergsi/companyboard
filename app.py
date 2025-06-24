import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Company Monthly Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar
st.sidebar.title("📅 Monthly Dashboard")
menu = ["Finances Revenue", "Supply Chain", "Sales"]
choice = st.sidebar.radio("Select section:", menu)

# Main Title
st.title("📊 Company Monthly Dashboard")

# Main content based on selection
if choice == "Finances Revenue":
    st.subheader("💰 Finances Revenue Overview")
    st.info("Here you can display revenue data and charts.")
    # Placeholder for future data

elif choice == "Supply Chain":
    st.subheader("🚛 Supply Chain Overview")
    st.info("Here you can display supply chain data and metrics.")
    # Placeholder for future data

elif choice == "Sales":
    st.subheader("🛒 Sales Overview")
    st.info("Here you can display sales data and summaries.")
    # Placeholder for future data
