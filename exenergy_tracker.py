import streamlit as st
import pandas as pd
from db import get_supabase

supabase = get_supabase()


def energy_tracker_page(user_id):

    st.title("⚡ Energy System (Split Model)")

    # =====================================================
    # ⚙️ ENERGY SETTINGS
    # =====================================================
    st.header("⚙️ Tariff Settings")

    with st.form("settings"):

        normal_rate = st.number_input("Normal Rate (Rs/unit)", min_value=0.0)
        peak_rate = st.number_input("Peak Rate (Rs/unit)", min_value=0.0)
        month = st.text_input("Month (e.g. Jan 2026)")

        submit = st.form_submit_button("Save Settings")

    if submit:
        supabase.table("energy_settings").insert({
            "user_id": user_id,
            "normal_rate": normal_rate,
            "peak_rate": peak_rate,
            "month": month
        }).execute()

        st.success("Saved!")
        st.rerun()

    st.divider()

    # =====================================================
    # 📄 BILL READINGS
    # =====================================================
    st.header("📄 Bill Reading (Monthly)")

    with st.form("bill_form"):

        start = st.date_input("Bill Start Date")
        end = st.date_input("Bill End Date")

        imp = st.number_input("Import Units (This Bill)")
        exp = st.number_input("Export Units (This Bill)")
        peak = st.number_input("Peak Units (This Bill)")

        export_cap = st.number_input("Export Cap (Units allowed)", min_value=0.0)

        submit = st.form_submit_button("Save Bill")

    if submit:
        supabase.table("bill_readings").insert({
            "user_id": user_id,
            "bill_start_date": str(start),
            "bill_end_date": str(end),
            "import_units": imp,
            "export_units": exp,
            "peak_import_units": peak,
            "export_cap": export_cap
        }).execute()

        st.success("Bill saved!")
        st.rerun()

    # =====================================================
    # 💰 ENERGY BALANCE
    # =====================================================
    st.header("💰 Energy Balance (Credit Tracking)")

    with st.form("balance_form"):

        reading_date = st.date_input("Date")

        prev = st.number_input("Previous Balance", min_value=0.0)
        curr = st.number_input("Current Balance", min_value=0.0)

        note = st.text_input("Note (optional)")

        submit = st.form_submit_button("Save Balance")

    if submit:

        supabase.table("energy_balance").insert({
            "user_id": user_id,
            "reading_date": str(reading_date),
            "previous_balance": prev,
            "current_balance": curr,
            "note": note
        }).execute()

        st.success("Balance saved!")
        st.rerun()

    # =====================================================
    # 🔌 METER SNAPSHOTS
    # =====================================================
    st.header("🔌 Meter Snapshot (Occasional)")

    with st.form("meter_form"):

        date = st.date_input("Reading Date")

        imp = st.number_input("Import Units", min_value=0.0, key="m1")
        exp = st.number_input("Export Units", min_value=0.0, key="m2")
        peak = st.number_input("Peak Units", min_value=0.0, key="m3")

        notes = st.text_input("Notes")

        submit = st.form_submit_button("Save Snapshot")

    if submit:
        supabase.table("meter_snapshots").insert({
            "user_id": user_id,
            "reading_date": str(date),
            "import_units": imp,
            "export_units": exp,
            "peak_import_units": peak,
            "notes": notes
        }).execute()

        st.success("Snapshot saved!")
        st.rerun()

    st.divider()

    # =====================================================
    # 🌞 SOLAR DAILY
    # =====================================================
    st.header("🌞 Solar Generation")

    with st.form("solar_form"):

        date = st.date_input("Date", key="s1")
        gen = st.number_input("Generated Units (kWh)", min_value=0.0)
        notes = st.text_input("Notes", key="s2")

        submit = st.form_submit_button("Save Solar")

    if submit:
        supabase.table("solar_daily").insert({
            "user_id": user_id,
            "reading_date": str(date),
            "generated_units": gen,
            "notes": notes
        }).execute()

        st.success("Solar saved!")
        st.rerun()

    st.divider()

    # =====================================================
    # 📊 QUICK VIEW
    # =====================================================

    st.header("📊 Recent Data")

    bills = supabase.table("bill_readings") \
        .select("*") \
        .eq("user_id", user_id) \
        .order("bill_end_date", desc=True) \
        .execute().data

    if bills:
        st.subheader("Latest Bills")
        st.dataframe(pd.DataFrame(bills))

    snapshots = supabase.table("meter_snapshots") \
        .select("*") \
        .eq("user_id", user_id) \
        .order("reading_date", desc=True) \
        .execute().data

    if snapshots:
        st.subheader("Latest Snapshots")
        st.dataframe(pd.DataFrame(snapshots))

    solar = supabase.table("solar_daily") \
        .select("*") \
        .eq("user_id", user_id) \
        .order("reading_date", desc=True) \
        .execute().data

    if solar:
        st.subheader("Solar History")
        st.dataframe(pd.DataFrame(solar))