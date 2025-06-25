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

        # Split into groups
        below_df = df[df['Amount'] <= 200]
        above_df = df[df['Amount'] > 200]

        below_count = below_df.shape[0]
        above_count = above_df.shape[0]

        below_revenue = below_df['Amount'].sum()
        above_revenue = above_df['Amount'].sum()

        # Calmer professional colors
        colors = ['#90caf9', '#f48fb1']  # Light blue and soft pink

        #### Customer Rate Analysis Chart ####
        st.markdown("### 📊 Customer Rate Analysis")

        fig1, ax1 = plt.subplots(figsize=(4, 4))
        sizes_count = [below_count, above_count]

        wedges, texts, autotexts = ax1.pie(
            sizes_count,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 10}
        )

        ax1.set_title("Customer Rate Analysis")
        plt.tight_layout()
        st.pyplot(fig1)

        # Custom legend BELOW the chart
        st.markdown(
            """
            <div style="text-align: center;">
            <span style="color:#90caf9; font-weight:bold;">⬤ ≤ $200</span> &nbsp;&nbsp;
            <span style="color:#f48fb1; font-weight:bold;">⬤ > $200</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        # ✅ Add count labels after chart
        st.write(f"Total customers ≤ $200: **{below_count}**")
        st.write(f"Total customers > $200: **{above_count}**")

        buf1 = io.BytesIO()
        fig1.savefig(buf1, format="jpeg", dpi=150, bbox_inches='tight')
        st.download_button("Download Customer Rate Chart", data=buf1.getvalue(),
                           file_name="customer_rate.jpeg", mime="image/jpeg")

        #### Revenue Percentage Impact Chart ####
        st.markdown("### 📊 Revenue Percentage Impact")

        # Compute revenue impact using min revenue / total revenue
        min_revenue = df['Amount'].min()
        impact_percentage = (min_revenue / total) * 100

        sizes_revenue = [below_revenue, above_revenue]

        fig2, ax2 = plt.subplots(figsize=(4, 4))
        wedges2, texts2, autotexts2 = ax2.pie(
            sizes_revenue,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 10}
        )

        ax2.set_title("Revenue Percentage Impact")
        plt.tight_layout()
        st.pyplot(fig2)

        # Custom legend BELOW the chart
        st.markdown(
            """
            <div style="text-align: center;">
            <span style="color:#90caf9; font-weight:bold;">⬤ ≤ $200</span> &nbsp;&nbsp;
            <span style="color:#f48fb1; font-weight:bold;">⬤ > $200</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(f"**Minimum Revenue Impact:** {impact_percentage:.2f}%")

        buf2 = io.BytesIO()
        fig2.savefig(buf2, format="jpeg", dpi=150, bbox_inches='tight')
        st.download_button("Download Revenue Impact Chart", data=buf2.getvalue(),
                           file_name="revenue_impact.jpeg", mime="image/jpeg")

    #### Form to add new revenue data ####
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
