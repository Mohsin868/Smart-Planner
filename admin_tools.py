import streamlit as st
from db import get_supabase

supabase = get_supabase()


def admin_panel(user_id):

    st.title("🧰 Admin Tools (Danger Zone)")

    st.warning("⚠️ These actions permanently delete data")

    # =====================================================
    # 📄 BILL READINGS
    # =====================================================
    st.subheader("📄 Bill Readings")

    bills = supabase.table("bill_readings") \
        .select("*") \
        .eq("user_id", user_id) \
        .execute().data

    if bills:
        for b in bills:
            col1, col2 = st.columns([4, 1])

            col1.write(f"{b['bill_start_date']} → {b['bill_end_date']} | Import: {b['import_units']}")

            if col2.button("🗑️", key=f"del_bill_{b['id']}"):
                supabase.table("bill_readings") \
                    .delete() \
                    .eq("id", b["id"]) \
                    .execute()
                st.rerun()

    if st.button("❌ Delete ALL Bills"):
        supabase.table("bill_readings") \
            .delete() \
            .eq("user_id", user_id) \
            .execute()
        st.success("All bills deleted")
        st.rerun()

    st.divider()

    # =====================================================
    # 🔌 METER SNAPSHOTS
    # =====================================================
    st.subheader("🔌 Meter Snapshots")

    meters = supabase.table("meter_snapshots") \
        .select("*") \
        .eq("user_id", user_id) \
        .execute().data

    if meters:
        for m in meters:
            col1, col2 = st.columns([4, 1])

            col1.write(f"{m['reading_date']} | Import: {m['import_units']}")

            if col2.button("🗑️", key=f"del_meter_{m['id']}"):
                supabase.table("meter_snapshots") \
                    .delete() \
                    .eq("id", m["id"]) \
                    .execute()
                st.rerun()

    if st.button("❌ Delete ALL Meter Snapshots"):
        supabase.table("meter_snapshots") \
            .delete() \
            .eq("user_id", user_id) \
            .execute()
        st.success("All snapshots deleted")
        st.rerun()

    st.divider()

    # =====================================================
    # 🌞 SOLAR DATA
    # =====================================================
    st.subheader("🌞 Solar Daily")

    solar = supabase.table("solar_daily") \
        .select("*") \
        .eq("user_id", user_id) \
        .execute().data

    if solar:
        for s in solar:
            col1, col2 = st.columns([4, 1])

            col1.write(f"{s['reading_date']} | Generated: {s['generated_units']}")

            if col2.button("🗑️", key=f"del_solar_{s['id']}"):
                supabase.table("solar_daily") \
                    .delete() \
                    .eq("id", s["id"]) \
                    .execute()
                st.rerun()

    if st.button("❌ Delete ALL Solar Data"):
        supabase.table("solar_daily") \
            .delete() \
            .eq("user_id", user_id) \
            .execute()
        st.success("All solar data deleted")
        st.rerun()

    st.divider()

    # =====================================================
    # 💰 ENERGY BALANCE
    # =====================================================
    st.subheader("💰 Energy Balance")

    balance = supabase.table("energy_balance") \
        .select("*") \
        .eq("user_id", user_id) \
        .execute().data

    if balance:
        for b in balance:
            col1, col2 = st.columns([4, 1])

            col1.write(f"{b['reading_date']} | {b['previous_balance']} → {b['current_balance']}")

            if col2.button("🗑️", key=f"del_bal_{b['id']}"):
                supabase.table("energy_balance") \
                    .delete() \
                    .eq("id", b["id"]) \
                    .execute()
                st.rerun()

    if st.button("❌ Delete ALL Balance Data"):
        supabase.table("energy_balance") \
            .delete() \
            .eq("user_id", user_id) \
            .execute()
        st.success("All balance data deleted")
        st.rerun()