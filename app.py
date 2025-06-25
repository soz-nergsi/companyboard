import io
import matplotlib.pyplot as plt

# ... (your previous code stays unchanged)

# Finances Revenue Page
if st.session_state.page == "Finances Revenue":
    st.subheader("💰 Finances Revenue Overview")
    revenue_df = load_revenue()
    st.dataframe(revenue_df, use_container_width=True)

    if not revenue_df.empty:
        total_revenue = revenue_df['Amount'].sum()
        st.metric("Total Revenue", f"${total_revenue:,.2f}")

        # Customer Rate Analysis
        below_200 = revenue_df[revenue_df['Amount'] <= 200].shape[0]
        above_200 = revenue_df[revenue_df['Amount'] > 200].shape[0]

        st.markdown("### 📊 Customer Rate Analysis")
        fig1, ax1 = plt.subplots(figsize=(3, 3))  # Smaller size
        ax1.pie([below_200, above_200],
                labels=['≤ 200', '> 200'],
                autopct='%1.1f%%',
                startangle=90)
        ax1.set_title("Customer Distribution")
        st.pyplot(fig1)

        # Download customer chart
        buf1 = io.BytesIO()
        fig1.savefig(buf1, format="jpeg", dpi=150, bbox_inches='tight')
        st.download_button("Download Customer Chart", data=buf1.getvalue(),
                           file_name="customer_distribution.jpeg", mime="image/jpeg")

        st.write(f"Total Customers: {below_200 + above_200}")
        st.write(f"Customers ≤ 200: {below_200}")
        st.write(f"Customers > 200: {above_200}")

        # Revenue Impact Analysis
        min_revenue = revenue_df['Amount'].min()
        impact_value = (min_revenue / total_revenue) * 100

        st.markdown("### 📊 Revenue Impact")
        fig2, ax2 = plt.subplots(figsize=(3, 3))  # Smaller size
        ax2.pie([min_revenue, total_revenue - min_revenue],
                labels=[f'Minimum Revenue ({impact_value:.1f}%)', 'Other'],
                autopct='%1.1f%%',
                startangle=90)
        ax2.set_title("Revenue Impact")
        st.pyplot(fig2)

        # Download revenue impact chart
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
