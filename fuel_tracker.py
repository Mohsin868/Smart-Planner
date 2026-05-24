import streamlit as st
import pandas as pd
from db import get_supabase

supabase = get_supabase()


def fuel_tracker_page(user_id):

    st.title("🚗 Vehicle Manager")

    # =====================================================
    # ADD VEHICLE
    # =====================================================

    st.subheader("➕ Add Vehicle")

    with st.form("vehicle_form"):

        vehicle_name = st.text_input("Vehicle Name")

        vehicle_type = st.selectbox(
            "Vehicle Type",
            ["Car", "Bike", "SUV", "Other"]
        )

        add_vehicle = st.form_submit_button("Add Vehicle")

    if add_vehicle:

        if vehicle_name.strip():

            supabase.table("vehicles").insert({
                "user_id": user_id,
                "vehicle_name": vehicle_name,
                "vehicle_type": vehicle_type
            }).execute()

            st.success("✅ Vehicle added!")
            st.rerun()

    st.divider()

    # =====================================================
    # LOAD VEHICLES
    # =====================================================

    vehicles_response = (
        supabase.table("vehicles")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )

    vehicles = vehicles_response.data

    if not vehicles:
        st.info("Add a vehicle first.")
        return

    vehicle_map = {
        f"{v['vehicle_name']} ({v['vehicle_type']})": v["id"]
        for v in vehicles
    }

    selected_vehicle = st.selectbox(
        "Select Vehicle",
        list(vehicle_map.keys())
    )

    vehicle_id = vehicle_map[selected_vehicle]

    # =====================================================
    # ADD FUEL ENTRY
    # =====================================================

    st.subheader("⛽ Add Fuel Entry")

    with st.form("fuel_form"):

        distance = st.number_input(
            "Distance Driven (km)",
            min_value=0.0,
            step=1.0
        )

        liters = st.number_input(
            "Fuel Filled (Liters)",
            min_value=0.1,
            step=0.1
        )

        cost = st.number_input(
            "Fuel Cost (PKR)",
            min_value=0.0,
            step=100.0
        )

        fuel_submit = st.form_submit_button("Save Fuel Entry")

    if fuel_submit:

        fuel_average = round(distance / liters, 2)
        cost_per_liter = round(cost / liters, 2)

        supabase.table("fuel_logs").insert({
            "user_id": user_id,
            "vehicle_id": vehicle_id,
            "distance": distance,
            "liters": liters,
            "cost": cost,
            "fuel_average": fuel_average,
            "cost_per_liter": cost_per_liter
        }).execute()

        st.success("✅ Fuel entry saved!")
        st.rerun()

    st.divider()

    # =====================================================
    # OIL CHANGE
    # =====================================================

    st.subheader("🛢️ Oil Change")

    with st.form("oil_form"):

        oil_type = st.text_input("Oil Type")

        odometer = st.number_input(
            "Current KM",
            min_value=0.0,
            step=100.0
        )

        next_change = st.number_input(
            "Next Oil Change KM",
            min_value=0.0,
            step=100.0
        )

        oil_cost = st.number_input(
            "Oil Change Cost",
            min_value=0.0,
            step=100.0
        )

        oil_submit = st.form_submit_button("Save Oil Change")

    if oil_submit:

        supabase.table("oil_changes").insert({
            "user_id": user_id,
            "vehicle_id": vehicle_id,
            "oil_type": oil_type,
            "odometer": odometer,
            "next_change_km": next_change,
            "cost": oil_cost
        }).execute()

        st.success("✅ Oil change saved!")
        st.rerun()

    st.divider()

    # =====================================================
    # LOAD FUEL LOGS
    # =====================================================

    fuel_response = (
        supabase.table("fuel_logs")
        .select("*")
        .eq("user_id", user_id)
        .eq("vehicle_id", vehicle_id)
        .order("created_at", desc=True)
        .execute()
    )

    fuel_data = fuel_response.data

    st.subheader("📊 Fuel History")

    if fuel_data:

        df = pd.DataFrame(fuel_data)

        st.dataframe(
            df[[
                "created_at",
                "distance",
                "liters",
                "cost",
                "fuel_average",
                "cost_per_liter"
            ]],
            use_container_width=True
        )

        # ================= ANALYTICS =================

        st.subheader("📈 Analytics")

        averages = df["fuel_average"]

        monthly_expense = df["cost"].sum()

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "⛽ Best Average",
            f"{averages.max():.2f} km/L"
        )

        col2.metric(
            "📉 Worst Average",
            f"{averages.min():.2f} km/L"
        )

        col3.metric(
            "💰 Total Fuel Expense",
            f"PKR {monthly_expense:,.0f}"
        )

        st.line_chart(averages)

    else:
        st.info("No fuel logs yet.")

    st.divider()

    # =====================================================
    # OIL HISTORY
    # =====================================================

    oil_response = (
        supabase.table("oil_changes")
        .select("*")
        .eq("user_id", user_id)
        .eq("vehicle_id", vehicle_id)
        .order("created_at", desc=True)
        .execute()
    )

    oil_data = oil_response.data

    st.subheader("🛢️ Oil Change History")

    if oil_data:

        oil_df = pd.DataFrame(oil_data)

        st.dataframe(
            oil_df[[
                "created_at",
                "oil_type",
                "odometer",
                "next_change_km",
                "cost"
            ]],
            use_container_width=True
        )

    else:
        st.info("No oil changes logged yet.")