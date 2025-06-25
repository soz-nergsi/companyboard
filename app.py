import streamlit as st

st.set_page_config(page_title="Company Monthly Dashboard", layout="wide")

st.sidebar.title("📊 Monthly Dashboard Navigation")

# Use radio instead of buttons
page = st.sidebar.radio(
    "Go to section:",
    ["🏦 Finances Revenue", "🚛 Supply Chain", "🛒 Sales"]
)

if page == "🏦 Finances Revenue":
    import revenue
    revenue.render()

elif page == "🚛 Supply Chain":
    import supply_chain
    supply_chain.render()

elif page == "🛒 Sales":
    import sales
    sales.render()
