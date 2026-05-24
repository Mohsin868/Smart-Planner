import streamlit as st
import pandas as pd
from db import get_supabase

supabase = get_supabase()


def energy_tracker_page(user_id):

    st.title("⚡ Simple Energy Tracker")

    # =====================================================
    # 📄 BILL READING (BASELINE)
    # =====================================================
    st.header("📄 Bill Meter Reading (Baseline)")

    with st.form("bill_form"):

        bill_date = st.date_input("Bill Date")

        bill_import = st.number_input("Import Units")
        bill_export = st.number_input("Export Units")
        bill_peak = st.number_input("Peak Units")

        submit = st.form_submit_button("Save Bill Reading")

    if submit:
        supabase.table("bill_readings").insert({
            "user_id": user_id,
            "bill_start_date": str(bill_date),
            "bill_end_date": str(bill_date),
            "import_units": bill_import,
            "export_units": bill_export,
            "peak_import_units": bill_peak
        }).execute()

        st.success("Bill saved!")
        st.rerun()

    st.divider()

    # =====================================================
    # 🔌 CURRENT METER READING
    # =====================================================
    st.header("🔌 Current Meter Reading")

    with st.form("current_form"):

        cur_date = st.date_input("Current Reading Date")

        cur_import = st.number_input("Import Units", key="c1")
        cur_export = st.number_input("Export Units", key="c2")
        cur_peak = st.number_input("Peak Units", key="c3")

        submit2 = st.form_submit_button("Save Current Reading")

    if submit2:
        supabase.table("meter_snapshots").insert({
            "user_id": user_id,
            "reading_date": str(cur_date),
            "import_units": cur_import,
            "export_units": cur_export,
            "peak_import_units": cur_peak
        }).execute()

        st.success("Current reading saved!")
        st.rerun()

    st.divider()

    # =====================================================
    # 📦 TOTAL USAGE SINCE BILL
    # =====================================================

    st.header("📦 Total Usage Since Last Bill")

    bills = supabase.table("bill_readings") \
        .select("*") \
        .eq("user_id", user_id) \
        .order("bill_end_date", desc=True) \
        .execute().data

    currents = supabase.table("meter_snapshots") \
        .select("*") \
        .eq("user_id", user_id) \
        .order("reading_date", desc=True) \
        .execute().data

    if bills and currents:

        latest_bill = bills[0]
        latest_current = currents[0]

        import_total = latest_current["import_units"] - latest_bill["import_units"]
        export_total = latest_current["export_units"] - latest_bill["export_units"]
        peak_total = latest_current["peak_import_units"] - latest_bill["peak_import_units"]

        col1, col2, col3 = st.columns(3)

        col1.metric("🔌 Total Import Used", f"{import_total:.2f}")
        col2.metric("⚡ Total Export Change", f"{export_total:.2f}")
        col3.metric("🔥 Total Peak Usage", f"{peak_total:.2f}")

    else:
        st.info("Add both bill and current readings to see total usage")

    st.divider()

    # =====================================================
    # 📊 PROGRESS TRACKING
    # =====================================================

    st.header("📊 Usage Progress Over Time")

    currents = supabase.table("meter_snapshots") \
        .select("*") \
        .eq("user_id", user_id) \
        .order("reading_date", desc=False) \
        .execute().data

    if len(currents) < 2:
        st.info("Add at least 2 meter readings to see progress.")
        st.stop()

    # =====================================================
    # 👁️ TOGGLE FOR FULL READINGS (NEW ADDITION)
    # =====================================================
    show_full = st.toggle("👁️ Show full meter readings", value=False)

    st.subheader("📈 Step-by-step Consumption")

    for i in range(1, len(currents)):

        prev = currents[i - 1]
        curr = currents[i]

        import_used = curr["import_units"] - prev["import_units"]
        export_used = curr["export_units"] - prev["export_units"]
        peak_used = curr["peak_import_units"] - prev["peak_import_units"]

        st.markdown(
            f"### 📅 {prev['reading_date']} → {curr['reading_date']}"
        )

        col1, col2, col3 = st.columns(3)

        col1.metric("🔌 Import Used", f"{import_used:.2f}")
        col2.metric("⚡ Export Change", f"{export_used:.2f}")
        col3.metric("🔥 Peak Used", f"{peak_used:.2f}")

        # =====================================================
        # 📟 FULL READINGS VIEW (TOGGLE ON)
        # =====================================================
        if show_full:

            st.markdown("#### 📟 Full Meter Readings")

            f1, f2 = st.columns(2)

            f1.write(f"**Previous Import:** {prev['import_units']}")
            f2.write(f"**Current Import:** {curr['import_units']}")

            f1.write(f"**Previous Export:** {prev['export_units']}")
            f2.write(f"**Current Export:** {curr['export_units']}")

            f1.write(f"**Previous Peak:** {prev['peak_import_units']}")
            f2.write(f"**Current Peak:** {curr['peak_import_units']}")

        st.divider()