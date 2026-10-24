"""
Smart Bus Ticket Booking & Reservation System
Streamlit Web Application (app.py)

A modern, university-hackathon ready web application for managing bus routes,
seat reservations, cancellations, schedules, and financial reports.
State is preserved within Streamlit session state (st.session_state).
"""

import streamlit as st
import pandas as pd
from bus_functions import (
    SUPPORTED_CITIES,
    get_initial_routes,
    get_route_status,
    calculate_occupied_seats,
    find_route_by_id,
    search_routes,
    filter_available_routes,
    validate_booking_inputs,
    calculate_fare,
    book_ticket,
    cancel_booking,
    get_route_schedules,
    calculate_dashboard_metrics,
    generate_report_text,
    sort_routes,
    sort_bookings
)

# Page configuration
st.set_page_config(
    page_title="Smart Bus Reservation System",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "routes" not in st.session_state:
    st.session_state.routes = get_initial_routes()

if "bookings" not in st.session_state:
    st.session_state.bookings = []

if "issued_ids" not in st.session_state:
    st.session_state.issued_ids = set()


# ---------------------------------------------------------
# Sidebar & Navigation
# ---------------------------------------------------------
with st.sidebar:
    st.title("🚌 Smart Bus Express")
    st.caption("University Hackathon Project | Fast & In-Memory System")
    st.markdown("---")

    menu_option = st.radio(
        "Navigation Menu",
        options=[
            "📊 Dashboard",
            "🚌 View Available Routes",
            "🔍 Search Routes",
            "🎫 Book a Ticket",
            "📋 View My Bookings",
            "❌ Cancel a Booking",
            "💺 View Seat Availability",
            "📅 Route Schedules",
            "📑 Booking Reports"
        ],
        index=0
    )

    st.markdown("---")
    st.subheader("⚙️ Session Management")
    if st.button("🔄 Reset System to Default", help="Clear all bookings and reset route seats"):
        st.session_state.routes = get_initial_routes()
        st.session_state.bookings = []
        st.session_state.issued_ids = set()
        st.toast("System has been reset to default initial state!", icon="🔄")
        st.rerun()

    st.info(
        "**Session Storage Notice:**\n"
        "Data is stored in-memory using `st.session_state`. Bookings and availability "
        "persist during your active session but reset when the server restarts."
    )


# ---------------------------------------------------------
# Helper Formatting Functions
# ---------------------------------------------------------
def format_currency(amount: int) -> str:
    """Format numeric amount into Pakistani Rupees (Rs.)."""
    return f"Rs. {amount:,}"


def status_badge(status: str) -> str:
    """Return an emoji and text badge for route and booking statuses."""
    if status == "Available":
        return "🟢 Available"
    elif status == "Partially Booked":
        return "🟡 Partially Booked"
    elif status == "Fully Booked":
        return "🔴 Fully Booked"
    elif status == "Confirmed":
        return "✅ Confirmed"
    elif status == "Cancelled":
        return "❌ Cancelled"
    return status


# ---------------------------------------------------------
# Feature A: Dashboard
# ---------------------------------------------------------
if menu_option == "📊 Dashboard":
    st.title("📊 Executive Dashboard")
    st.markdown("Welcome to the **Smart Bus Ticket Booking & Reservation System**.")

    metrics = calculate_dashboard_metrics(st.session_state.routes, st.session_state.bookings)

    # Top KPI Metrics Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Active Routes", value=metrics["total_routes"])
    with col2:
        st.metric(label="Total Seat Capacity", value=metrics["total_capacity"])
    with col3:
        st.metric(label="Available Seats", value=metrics["available_seats"], delta=f"{metrics['available_seats']} left")
    with col4:
        st.metric(label="Occupied Seats", value=metrics["occupied_seats"])

    st.markdown("---")

    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.metric(label="Confirmed Bookings", value=metrics["confirmed_bookings"])
    with col6:
        st.metric(label="Cancelled Bookings", value=metrics["cancelled_bookings"])
    with col7:
        st.metric(label="Confirmed Revenue", value=format_currency(metrics["confirmed_revenue"]))
    with col8:
        st.metric(label="Fully Booked Routes", value=metrics["fully_booked_routes"])

    st.markdown("---")

    # Quick Route Snapshot
    st.subheader("🚌 Live Route Availability Snapshot")
    snapshot_rows = []
    for idx, r in enumerate(st.session_state.routes, start=1):
        status = get_route_status(r)
        occupied = calculate_occupied_seats(r)
        snapshot_rows.append({
            "No.": idx,
            "Route ID": r["route_id"],
            "Departure": r["departure_city"],
            "Destination": r["destination_city"],
            "Departure Time": r["departure_time"],
            "Fare per Seat": format_currency(r["ticket_price"]),
            "Seats (Avail/Total)": f"{r['available_seats']} / {r['total_seats']}",
            "Occupied": occupied,
            "Status": status_badge(status)
        })

    st.dataframe(pd.DataFrame(snapshot_rows), hide_index=True, use_container_width=True)

    # Quick summary tips
    with st.expander("💡 Understanding System State Calculations"):
        st.write("""
        - **Confirmed Revenue:** Calculated solely from confirmed reservations. Cancelled bookings are strictly excluded.
        - **Seat Availability:** Synced in real time upon successful booking or cancellation.
        - **Data Integrity:** Availability is prevented from dropping below 0 or exceeding original coach capacity.
        """)


# ---------------------------------------------------------
# Feature B: View Available Routes
# ---------------------------------------------------------
elif menu_option == "🚌 View Available Routes":
    st.title("🚌 Bus Routes Catalog")
    st.markdown("Browse all scheduled bus routes, departures, fares, and current availability.")

    col_filter, col_sort = st.columns([1, 1])
    with col_filter:
        only_available = st.checkbox("Show only routes with available seats", value=False)
    with col_sort:
        sort_choice = st.selectbox(
            "Sort Routes By",
            options=["Route ID", "Lowest Fare", "Highest Fare", "Most Available Seats"]
        )

    # Filter logic using continue
    display_routes = []
    for route in st.session_state.routes:
        if only_available and route["available_seats"] <= 0:
            continue
        display_routes.append(route)

    # Sorting using lambda functions
    if sort_choice == "Lowest Fare":
        display_routes = sort_routes(display_routes, key_name="ticket_price", reverse=False)
    elif sort_choice == "Highest Fare":
        display_routes = sort_routes(display_routes, key_name="ticket_price", reverse=True)
    elif sort_choice == "Most Available Seats":
        display_routes = sort_routes(display_routes, key_name="available_seats", reverse=True)
    else:
        display_routes = sort_routes(display_routes, key_name="route_id", reverse=False)

    if not display_routes:
        st.warning("No routes match your current filter.")
    else:
        table_data = []
        for index, r in enumerate(display_routes, start=1):
            table_data.append({
                "No.": index,
                "Route ID": r["route_id"],
                "Journey": f"{r['departure_city']} ➔ {r['destination_city']}",
                "Departure Time": r["departure_time"],
                "Fare per Seat": format_currency(r["ticket_price"]),
                "Available Seats": r["available_seats"],
                "Total Capacity": r["total_seats"],
                "Status": status_badge(get_route_status(r))
            })
        st.dataframe(pd.DataFrame(table_data), hide_index=True, use_container_width=True)


# ---------------------------------------------------------
# Feature C: Search Routes
# ---------------------------------------------------------
elif menu_option == "🔍 Search Routes":
    st.title("🔍 Search Bus Routes")
    st.markdown("Search for journeys by **Route ID** (e.g. `R101`) or by **City** (e.g. `Karachi`, `Hyderabad`).")

    search_query = st.text_input("Enter Route ID or City Name:", placeholder="e.g. Hyderabad, Karachi, R104").strip()

    if search_query:
        matches = search_routes(st.session_state.routes, search_query)
        if matches:
            st.success(f"Found {len(matches)} matching route(s) for '{search_query}':")
            results_data = []
            for idx, r in enumerate(matches, start=1):
                results_data.append({
                    "No.": idx,
                    "Route ID": r["route_id"],
                    "Departure": r["departure_city"],
                    "Destination": r["destination_city"],
                    "Departure Time": r["departure_time"],
                    "Fare per Seat": format_currency(r["ticket_price"]),
                    "Available Seats": f"{r['available_seats']} / {r['total_seats']}",
                    "Status": status_badge(get_route_status(r))
                })
            st.dataframe(pd.DataFrame(results_data), hide_index=True, use_container_width=True)
        else:
            st.warning(f"No routes found matching '{search_query}'. Please verify spelling or try another city.")
    else:
        st.info("Please enter a search keyword above to inspect available journeys.")


# ---------------------------------------------------------
# Feature D: Book a Ticket
# ---------------------------------------------------------
elif menu_option == "🎫 Book a Ticket":
    st.title("🎫 Reserve Bus Tickets")
    st.markdown("Enter passenger information and select your preferred route to reserve seats.")

    # Build options for route selection
    route_options = {}
    for r in st.session_state.routes:
        status_text = "AVAILABLE" if r["available_seats"] > 0 else "FULL"
        label = f"{r['route_id']} : {r['departure_city']} ➔ {r['destination_city']} ({r['departure_time']}) | Fare: Rs. {r['ticket_price']:,} | {r['available_seats']} seats left [{status_text}]"
        route_options[label] = r["route_id"]

    with st.form("booking_form", clear_on_submit=False):
        col_name, col_age = st.columns(2)
        with col_name:
            passenger_name = st.text_input("Passenger Full Name *", placeholder="e.g. Ahmed Khan")
        with col_age:
            passenger_age_input = st.number_input("Passenger Age *", min_value=1, max_value=120, value=25, step=1)

        selected_label = st.selectbox("Select Bus Route *", options=list(route_options.keys()))
        selected_route_id = route_options[selected_label]
        selected_route = find_route_by_id(st.session_state.routes, selected_route_id)

        col_seats, col_fare_preview = st.columns(2)
        with col_seats:
            seats_requested = st.number_input("Number of Seats to Reserve *", min_value=1, max_value=50, value=1, step=1)

        with col_fare_preview:
            if selected_route:
                calc_total = selected_route["ticket_price"] * seats_requested
                st.write("**Fare Estimation:**")
                st.write(f"Fare per Seat: **{format_currency(selected_route['ticket_price'])}**")
                st.write(f"Estimated Total: **{format_currency(calc_total)}**")

        submit_booking = st.form_submit_button("Confirm Reservation 🎟️", use_container_width=True)

    if submit_booking:
        success, result = book_ticket(
            routes=st.session_state.routes,
            bookings=st.session_state.bookings,
            issued_ids=st.session_state.issued_ids,
            passenger_name=passenger_name,
            passenger_age=passenger_age_input,
            route_id=selected_route_id,
            seat_count=seats_requested
        )

        if success:
            st.success("🎉 Booking Confirmed Successfully!")
            st.balloons()
            # Confirmation card
            st.markdown(f"""
            ### 🎫 Booking Confirmation Details
            - **Booking ID:** `{result['booking_id']}`
            - **Passenger Name:** **{result['passenger_name']}** (Age: {result['passenger_age']})
            - **Route:** **{result['route_id']}** ({result['journey']})
            - **Departure Time:** **{result['departure_time']}**
            - **Seats Booked:** **{result['seats']}** seat(s)
            - **Fare per Seat:** {format_currency(result['fare_per_seat'])}
            - **Total Fare Paid:** **{format_currency(result['total_fare'])}**
            - **Status:** {status_badge(result['status'])}
            """)
        else:
            st.error(f"❌ Booking Failed: {result}")


# ---------------------------------------------------------
# Feature E: View My Bookings
# ---------------------------------------------------------
elif menu_option == "📋 View My Bookings":
    st.title("📋 Booking History & Records")
    st.markdown("Inspect all reservations created during this session, including confirmed and cancelled records.")

    if not st.session_state.bookings:
        st.info("ℹ️ No bookings found in the current session. Use the **Book a Ticket** page to create reservations.")
    else:
        col_filter_status, col_filter_route = st.columns(2)
        with col_filter_status:
            status_filter = st.selectbox("Filter by Status", options=["All", "Confirmed", "Cancelled"])
        with col_filter_route:
            route_filter_options = ["All"] + [r["route_id"] for r in st.session_state.routes]
            route_filter = st.selectbox("Filter by Route ID", options=route_filter_options)

        filtered_bookings = []
        for b in st.session_state.bookings:
            if status_filter != "All" and b["status"] != status_filter:
                continue
            if route_filter != "All" and b["route_id"] != route_filter:
                continue
            filtered_bookings.append(b)

        if not filtered_bookings:
            st.warning("No booking records match your selected filter criteria.")
        else:
            st.write(f"Showing **{len(filtered_bookings)}** booking record(s):")
            b_table = []
            for idx, b in enumerate(filtered_bookings, start=1):
                b_table.append({
                    "No.": idx,
                    "Booking ID": b["booking_id"],
                    "Passenger Name": b["passenger_name"],
                    "Age": b["passenger_age"],
                    "Route ID": b["route_id"],
                    "Journey": b["journey"],
                    "Seats": b["seats"],
                    "Total Fare": format_currency(b["total_fare"]),
                    "Status": status_badge(b["status"])
                })
            st.dataframe(pd.DataFrame(b_table), hide_index=True, use_container_width=True)


# ---------------------------------------------------------
# Feature F: Cancel a Booking
# ---------------------------------------------------------
elif menu_option == "❌ Cancel a Booking":
    st.title("❌ Cancel Reservation")
    st.markdown("Cancel an active confirmed booking. Reserved seats will immediately be restored to the route.")

    # Find active confirmed bookings
    confirmed_bookings = [b for b in st.session_state.bookings if b["status"] == "Confirmed"]

    if not confirmed_bookings:
        st.info("There are currently no active confirmed bookings to cancel.")
    else:
        st.write("Select a booking from active reservations, or manually enter the Booking ID:")

        confirmed_dict = {
            f"{b['booking_id']} — {b['passenger_name']} ({b['journey']}, {b['seats']} seat(s), {format_currency(b['total_fare'])})": b["booking_id"]
            for b in confirmed_bookings
        }

        selected_key = st.selectbox("Select Active Booking", options=list(confirmed_dict.keys()))
        selected_id = confirmed_dict[selected_key]

        manual_id = st.text_input("Or enter Booking ID manually (e.g. B1001):", value=selected_id).strip()

        col_cancel_btn, _ = st.columns([1, 2])
        with col_cancel_btn:
            cancel_btn = st.button("Cancel Reservation ❌", type="primary", use_container_width=True)

        if cancel_btn:
            target_id = manual_id if manual_id else selected_id
            success, details = cancel_booking(
                routes=st.session_state.routes,
                bookings=st.session_state.bookings,
                booking_id=target_id
            )

            if success:
                st.success(f"✅ Booking **{details['booking_id']}** has been successfully cancelled!")
                st.info(
                    f"**Seats Restored:** {details['seats_restored']} seat(s)\n\n"
                    f"**Route {details['route_id']} New Availability:** {details['new_available_seats']} / {details['total_seats']} seats."
                )
            else:
                st.error(f"❌ Cancellation Failed: {details}")


# ---------------------------------------------------------
# Feature G: View Seat Availability
# ---------------------------------------------------------
elif menu_option == "💺 View Seat Availability":
    st.title("💺 Bus Seat Availability & Capacity")
    st.markdown("Real-time occupancy tracking across all scheduled bus routes.")

    filter_seats_remaining = st.checkbox("Show only routes with seats remaining", value=False)

    seat_data = []
    for idx, r in enumerate(st.session_state.routes, start=1):
        if filter_seats_remaining and r["available_seats"] <= 0:
            continue
        occupied = calculate_occupied_seats(r)
        total = r["total_seats"]
        occupancy_pct = round((occupied / total) * 100, 1) if total > 0 else 0
        seat_data.append({
            "No.": idx,
            "Route ID": r["route_id"],
            "Journey": f"{r['departure_city']} ➔ {r['destination_city']}",
            "Departure Time": r["departure_time"],
            "Total Capacity": total,
            "Occupied Seats": occupied,
            "Available Seats": r["available_seats"],
            "Occupancy Rate": f"{occupancy_pct}%",
            "Status": status_badge(get_route_status(r))
        })

    st.dataframe(pd.DataFrame(seat_data), hide_index=True, use_container_width=True)

    # Visual occupancy cards
    st.subheader("📊 Visual Coach Load")
    cols = st.columns(len(st.session_state.routes))
    for i, r in enumerate(st.session_state.routes):
        with cols[i]:
            occupied = calculate_occupied_seats(r)
            total = r["total_seats"]
            ratio = occupied / total if total > 0 else 0.0
            st.metric(label=f"Route {r['route_id']}", value=f"{r['available_seats']} left", delta=f"{occupied}/{total} booked", delta_color="inverse")
            st.progress(ratio)


# ---------------------------------------------------------
# Feature H: Booking Reports
# ---------------------------------------------------------
elif menu_option == "📑 Booking Reports":
    st.title("📑 Official Booking & Financial Report")
    st.markdown("Comprehensive operational summary and downloadable audit report.")

    metrics = calculate_dashboard_metrics(st.session_state.routes, st.session_state.bookings)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Bookings Created", metrics["total_bookings"])
        st.metric("Confirmed Bookings", metrics["confirmed_bookings"])
    with col2:
        st.metric("Cancelled Bookings", metrics["cancelled_bookings"])
        st.metric("Seats Currently Reserved", metrics["reserved_seats"])
    with col3:
        st.metric("Confirmed Revenue", format_currency(metrics["confirmed_revenue"]))
        st.metric("Fully Booked Routes", metrics["fully_booked_routes"])

    st.markdown("---")
    st.subheader("📄 Plain-Text Report Preview")
    report_text = generate_report_text(st.session_state.routes, st.session_state.bookings)
    st.text_area("Generated Report Content", value=report_text, height=350)

    # Download button
    st.download_button(
        label="📥 Download Official Report (.txt)",
        data=report_text,
        file_name="smart_bus_booking_report.txt",
        mime="text/plain",
        use_container_width=True
    )


# ---------------------------------------------------------
# Feature I: Route Schedules
# ---------------------------------------------------------
elif menu_option == "📅 Route Schedules":
    st.title("📅 Route Schedules by Departure City")
    st.markdown("Scheduled bus departures grouped by city of origin, built with nested loops.")

    schedules = get_route_schedules(st.session_state.routes, SUPPORTED_CITIES)

    for city in SUPPORTED_CITIES:
        routes_from_city = schedules.get(city, [])
        with st.container():
            st.subheader(f"📍 Departures from {city}")
            if not routes_from_city:
                st.caption("No scheduled departures.")
            else:
                city_rows = []
                for r in routes_from_city:
                    city_rows.append({
                        "Route ID": r["route_id"],
                        "Destination": r["destination_city"],
                        "Departure Time": r["departure_time"],
                        "Fare per Seat": format_currency(r["ticket_price"]),
                        "Total Seats": r["total_seats"],
                        "Available": r["available_seats"],
                        "Status": status_badge(get_route_status(r))
                    })
                st.dataframe(pd.DataFrame(city_rows), hide_index=True, use_container_width=True)
        st.markdown("---")
