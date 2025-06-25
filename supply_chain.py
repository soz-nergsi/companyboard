def render():
    st.subheader("🚛 Supply Chain Monthly Dashboard")

    df = load_data()
    st.dataframe(df, use_container_width=True)

    if not df.empty:
        # ✅ Always parse dates after full load
        df['PR'] = pd.to_datetime(df['PR'], errors='coerce')
        df['PO'] = pd.to_datetime(df['PO'], errors='coerce')
        df = df.dropna(subset=['PR', 'PO'])  # drop rows with bad dates

        # ✅ Calculate durations
        df['Duration'] = (df['PO'] - df['PR']).dt.days

        # ✅ Calculate correct metrics
        total_job_orders = df['Job Order'].nunique()
        average_days = df['Duration'].mean()

        st.markdown(f"**Total Unique Job Orders:** {total_job_orders}")
        st.markdown(f"**Overall Average Duration:** {average_days:.1f} days")

        # Optional: keep your monthly chart if you want
