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

        # Split groups
        below_df = df[df['Amount'] <= 200]
        above_df = df[df['Amount'] > 200]

        below_count = below_df.shape[0]
        above_count = above_df.shape[0]

        below_revenue = below_df['Amount'].sum()
        above_revenue = above_df['Amount'].sum()

        colors = ['#90caf9', '#f48fb1']  # Soft blue & pink

        #### Customer Rate Analysis ####
        st.markdown("### 📊 Customer Rate Analysis")

        sizes = [below_count, above_count]
        labels = ["≤ $200", "> $200"]

        fig1, ax1 = plt.subplots(figsize=(4, 4))
        wedges, texts, autotexts = ax1.pie(
            sizes,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 10},
            pctdistance=0.7
        )

        # External labels for counts
        for i, wedge in enumerate(wedges):
            ang = (wedge.theta2 + wedge.theta1) / 2.
            x = 1.1 * np.cos(np.deg2rad(ang))
            y = 1.1 * np.sin(np.deg2rad(ang))
            ax1.text(x, y, f"{sizes[i]} customers", ha='center', va='center', fontsize=9)

        ax1.set_title("Customer Rate Analysis")
        plt.tight_layout()
        st.pyplot(fig1)

        # Legend below
        st.markdown(
            """
            <div style="text-align: center;">
            <span style="color:#90caf9; font-weight:bold;">⬤ ≤ $200</span> &nbsp;&nbsp;
            <span style="color:#f48fb1; font-weight:bold;">⬤ > $200</span>
            </div>
            """, unsafe_allow_html=True
        )

        buf1 = io.BytesIO()
        fig1.savefig(buf1, format="jpeg", dpi=150, bbox_inches='tight')
        st.download_button("Download Customer Rate Chart", data=buf1.getvalue(),
                           file_name="customer_rate.jpeg", mime="image/jpeg")

        #### Revenue Percentage Impact ####
        st.markdown("### 📊 Revenue Percentage Impact")

        min_revenue = df['Amount'].min()
        impact_percentage = (min_revenue / total) * 100

        sizes_revenue = [below_revenue, above_revenue]

        fig2, ax2 = plt.subplots(figsize=(4, 4))
        wedges2, texts2, autotexts2 = ax2.pie(
            sizes_revenue,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 10},
            pctdistance=0.7
        )

        ax2.set_title("Revenue Percentage Impact")
        plt.tight_layout()
        st.pyplot(fig2)

        st.markdown(
            """
            <div style="text-align: center;">
            <span style="color:#90caf9; font-weight:bold;">⬤ ≤ $200</span> &nbsp;&nbsp;
            <span style="color:#f48fb1; font-weight:bold;">⬤ > $200</span>
            </div>
            """, unsafe_allow_html=True
        )

        st.markdown(f"**Minimum Revenue Impact:** {impact_percentage:.2f}%")

        buf2 = io.BytesIO()
        fig2.savefig(buf2, format="jpeg", dpi=150, bbox_inches='tight')
        st.download_button("Download Revenue Impact Chart", data=buf2.getvalue(),
                           file_name="revenue_impact.jpeg", mime="image/jpeg")

    #### Add Revenue Entry Form ####
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
