import streamlit as st

st.set_page_config(page_title="Company Monthly Dashboard", layout="wide")

st.sidebar.title("📊 Monthly Dashboard Navigation")

# Use radio button for stable navigation (sections always visible)
page = st.sidebar.radio(
    "Select section:",
    ("🏦 Finances Revenue", "🚛 Supply Chain", "🛒 Sales")
)

# Dynamic import based on selection
if page == "🏦 Finances Revenue":
    import revenue
    revenue.render()

elif page == "🚛 Supply Chain":
    import supply_chain
    supply_chain.render()

elif page == "🛒 Sales":
    import sales
    sales.render()
