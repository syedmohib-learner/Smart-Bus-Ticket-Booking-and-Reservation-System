"""
Smart Bus Ticket Booking & Reservation System
Module: bus_functions.py

This module contains the core business logic, data models, validation routines,
seat calculation rules, and report generators for the reservation system.
It utilizes core Python data structures (lists, dictionaries, tuples, sets)
and control flow constructs (loops, nested loops, enumerate, for-else, break, continue).
"""

from typing import List, Dict, Tuple, Set, Optional, Any
import copy

# Supported cities stored in an immutable Tuple
SUPPORTED_CITIES: Tuple[str, ...] = (
    "Karachi",
    "Hyderabad",
    "Sukkur",
    "Mirpur Khas",
    "Lahore"
)

# Initial starter routes configuration
DEFAULT_ROUTES: List[Dict[str, Any]] = [
    {
        "route_id": "R101",
        "departure_city": "Karachi",
        "destination_city": "Hyderabad",
        "departure_time": "08:00 AM",
        "ticket_price": 1200,
        "total_seats": 40,
        "available_seats": 40
    },
    {
        "route_id": "R102",
        "departure_city": "Karachi",
        "destination_city": "Sukkur",
        "departure_time": "09:30 AM",
        "ticket_price": 2000,
        "total_seats": 36,
        "available_seats": 36
    },
    {
        "route_id": "R103",
        "departure_city": "Hyderabad",
        "destination_city": "Mirpur Khas",
        "departure_time": "11:00 AM",
        "ticket_price": 800,
        "total_seats": 32,
        "available_seats": 32
    },
    {
        "route_id": "R104",
        "departure_city": "Karachi",
        "destination_city": "Lahore",
        "departure_time": "07:00 PM",
        "ticket_price": 5000,
        "total_seats": 45,
        "available_seats": 45
    },
    {
        "route_id": "R105",
        "departure_city": "Sukkur",
        "destination_city": "Hyderabad",
        "departure_time": "02:00 PM",
        "ticket_price": 1500,
        "total_seats": 30,
        "available_seats": 30
    }
]


def get_initial_routes() -> List[Dict[str, Any]]:
    """
    Return a fresh deep copy of the default bus routes.
    Ensures state isolation for tests and fresh sessions.
    """
    return copy.deepcopy(DEFAULT_ROUTES)


def get_route_status(route: Dict[str, Any]) -> str:
    """
    Determine the operational booking status of a route.
    Rules:
    - Available: all seats are available
    - Fully Booked: 0 seats remaining
    - Partially Booked: between 1 and (total - 1) seats available
    """
    avail = route.get("available_seats", 0)
    total = route.get("total_seats", 0)

    if avail == total:
        return "Available"
    elif avail == 0:
        return "Fully Booked"
    else:
        return "Partially Booked"


def calculate_occupied_seats(route: Dict[str, Any]) -> int:
    """
    Calculate occupied seats for a given route dictionary:
    occupied = total_seats - available_seats
    """
    return route.get("total_seats", 0) - route.get("available_seats", 0)


def find_route_by_id(routes: List[Dict[str, Any]], route_id: str) -> Optional[Dict[str, Any]]:
    """
    Find a route dictionary by its unique Route ID.
    Demonstrates case normalization, loop traversal, 'break', and 'for-else'.
    """
    cleaned_id = str(route_id).strip().upper()
    for route in routes:
        if route.get("route_id", "").upper() == cleaned_id:
            return route  # Match found; break early by returning
    else:
        # Executes only if the loop completed without encountering a match
        return None


def search_routes(routes: List[Dict[str, Any]], search_term: str) -> List[Dict[str, Any]]:
    """
    Search routes by Route ID, Departure City, or Destination City.
    Demonstrates:
    - String trimming and lowercasing for case-insensitive matching
    - Direct route ID exact lookup with 'break'
    - Partial or city-wide scan for departure and destination cities
    - 'for-else' structure
    """
    term = str(search_term).strip().lower()
    if not term:
        return []

    # Check for direct route ID match first
    matched_by_id = []
    for route in routes:
        if route.get("route_id", "").lower() == term:
            matched_by_id.append(route)
            break
    else:
        # If no route ID matched, search by departure and destination city
        pass

    if matched_by_id:
        return matched_by_id

    # Search by city names
    results: List[Dict[str, Any]] = []
    for route in routes:
        dep = route.get("departure_city", "").lower()
        dest = route.get("destination_city", "").lower()
        if term in dep or term in dest:
            results.append(route)

    return results


def filter_available_routes(routes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter and return routes that have at least one seat available.
    Demonstrates the use of 'continue' to skip fully booked routes.
    """
    available_list = []
    for route in routes:
        if route.get("available_seats", 0) <= 0:
            continue  # Skip fully booked routes
        available_list.append(route)
    return available_list


def generate_booking_id(issued_ids: Set[str]) -> str:
    """
    Generate a unique, readable booking identifier (e.g. B1001, B1002).
    Demonstrates a while loop with membership checking in a Python set.
    """
    counter = 1001
    while True:
        candidate = f"B{counter}"
        if candidate not in issued_ids:
            return candidate
        counter += 1


def validate_booking_inputs(
    passenger_name: Any,
    passenger_age: Any,
    route_id: Any,
    seat_count: Any,
    routes: List[Dict[str, Any]]
) -> Tuple[bool, Optional[str]]:
    """
    Validate all inputs before creating a reservation.
    Enforces business rules BR-01 through BR-05:
    - BR-01: Passenger name required (non-empty, non-whitespace).
    - BR-02: Age must be a positive integer (> 0).
    - BR-03: Route must exist in active route catalog.
    - BR-04: Seat quantity must be a positive integer (> 0).
    - BR-05: Requested seats must not exceed available seats.
    """
    # BR-01: Name check
    if not isinstance(passenger_name, str) or not passenger_name.strip():
        return False, "Passenger name cannot be empty or contain only whitespace."

    # BR-02: Age check
    try:
        age = int(passenger_age)
        if age <= 0:
            return False, "Passenger age must be a positive integer greater than zero."
    except (ValueError, TypeError):
        return False, "Passenger age must be a valid positive whole number."

    # BR-03: Route existence check
    route = find_route_by_id(routes, str(route_id))
    if route is None:
        return False, f"Route ID '{route_id}' does not exist in the system."

    # BR-04: Seat quantity check
    try:
        seats = int(seat_count)
        if seats <= 0:
            return False, "Requested seat quantity must be an integer greater than zero."
    except (ValueError, TypeError):
        return False, "Seat quantity must be a valid whole number."

    # BR-05: Availability check
    available = route.get("available_seats", 0)
    if seats > available:
        return False, (
            f"Cannot book {seats} seat(s). Route {route['route_id']} only has "
            f"{available} seat(s) available."
        )

    return True, None


def calculate_fare(price_per_seat: int, seats: int) -> int:
    """
    Calculate the total ticket fare.
    BR-07: Total fare = ticket_price * seats.
    """
    return price_per_seat * seats


def book_ticket(
    routes: List[Dict[str, Any]],
    bookings: List[Dict[str, Any]],
    issued_ids: Set[str],
    passenger_name: str,
    passenger_age: Any,
    route_id: str,
    seat_count: Any
) -> Tuple[bool, Any]:
    """
    Complete booking process:
    1. Validates all inputs safely.
    2. Calculates fare.
    3. Generates unique booking ID.
    4. Updates route seat availability exactly once.
    5. Records booking dictionary in bookings list.
    6. Adds booking ID to issued_ids set.

    Returns:
    - (True, booking_record_dict) on success
    - (False, error_message_string) on failure
    """
    # Run validation first
    is_valid, error_msg = validate_booking_inputs(
        passenger_name, passenger_age, route_id, seat_count, routes
    )
    if not is_valid:
        return False, error_msg

    # Retrieve route
    route = find_route_by_id(routes, route_id)
    if route is None:
        return False, f"Route '{route_id}' not found."

    seats = int(seat_count)
    age = int(passenger_age)
    clean_name = passenger_name.strip()

    # Calculate fare
    fare = calculate_fare(route["ticket_price"], seats)

    # Generate unique booking ID and register in set
    booking_id = generate_booking_id(issued_ids)
    issued_ids.add(booking_id)

    # Decrement available seats exactly once (BR-08, BR-13)
    route["available_seats"] -= seats

    # Create new booking record dictionary
    booking_record: Dict[str, Any] = {
        "booking_id": booking_id,
        "passenger_name": clean_name,
        "passenger_age": age,
        "route_id": route["route_id"],
        "departure_city": route["departure_city"],
        "destination_city": route["destination_city"],
        "journey": f"{route['departure_city']} -> {route['destination_city']}",
        "departure_time": route["departure_time"],
        "seats": seats,
        "fare_per_seat": route["ticket_price"],
        "total_fare": fare,
        "status": "Confirmed"
    }

    bookings.append(booking_record)
    return True, booking_record


def cancel_booking(
    routes: List[Dict[str, Any]],
    bookings: List[Dict[str, Any]],
    booking_id: str
) -> Tuple[bool, Any]:
    """
    Cancel an existing Confirmed booking:
    1. Finds the booking by ID.
    2. Rejects if not found.
    3. Rejects if already Cancelled (preventing double seat restoration).
    4. Restores reserved seats to the route once without exceeding total capacity.
    5. Sets status to 'Cancelled'.
    6. Retains the record in history.

    Returns:
    - (True, cancellation_details_dict) on success
    - (False, error_message_string) on failure
    """
    clean_id = str(booking_id).strip().upper()
    target_booking = None

    # Search for booking; demonstrates for-else
    for booking in bookings:
        if booking.get("booking_id", "").upper() == clean_id:
            target_booking = booking
            break
    else:
        return False, f"Booking ID '{clean_id}' was not found in existing records."

    # BR-09: Only Confirmed booking can be cancelled
    if target_booking.get("status") == "Cancelled":
        return False, f"Booking '{clean_id}' is already cancelled. Seats cannot be restored again."

    if target_booking.get("status") != "Confirmed":
        return False, f"Cannot cancel booking '{clean_id}' with status '{target_booking.get('status')}'."

    # Retrieve associated route
    route = find_route_by_id(routes, target_booking.get("route_id", ""))
    if route is None:
        return False, f"Associated route '{target_booking.get('route_id')}' could not be located."

    # BR-10 & BR-13: Restore seats safely (available_seats <= total_seats)
    seats_to_restore = target_booking.get("seats", 0)
    current_avail = route.get("available_seats", 0)
    total_capacity = route.get("total_seats", 0)

    restored_avail = min(current_avail + seats_to_restore, total_capacity)
    route["available_seats"] = restored_avail

    # BR-11: Retain record and update status
    target_booking["status"] = "Cancelled"

    details = {
        "booking_id": clean_id,
        "passenger_name": target_booking.get("passenger_name"),
        "route_id": route["route_id"],
        "journey": target_booking.get("journey"),
        "seats_restored": seats_to_restore,
        "new_available_seats": route["available_seats"],
        "total_seats": route["total_seats"]
    }
    return True, details


def get_route_schedules(
    routes: List[Dict[str, Any]],
    cities: Tuple[str, ...] = SUPPORTED_CITIES
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group routes by departure city using nested loops.
    Outer loop iterates through the supported cities tuple.
    Inner loop iterates through all routes to find matches.
    If a city has no departing routes, it maps to an empty list.
    """
    schedules: Dict[str, List[Dict[str, Any]]] = {}

    # Outer loop over supported cities
    for city in cities:
        city_routes: List[Dict[str, Any]] = []
        # Inner loop over route catalog
        for route in routes:
            if route.get("departure_city", "").lower() == city.lower():
                city_routes.append(route)
        schedules[city] = city_routes

    return schedules


def calculate_dashboard_metrics(
    routes: List[Dict[str, Any]],
    bookings: List[Dict[str, Any]]
) -> Dict[str, int]:
    """
    Calculate summary metrics dynamically from current state:
    - total_routes
    - total_capacity
    - available_seats
    - occupied_seats
    - confirmed_bookings
    - cancelled_bookings
    - total_bookings
    - confirmed_revenue (excludes cancelled bookings)
    - fully_booked_routes
    """
    total_routes = len(routes)
    total_capacity = 0
    available_seats = 0
    fully_booked_routes = 0

    for route in routes:
        total_capacity += route.get("total_seats", 0)
        avail = route.get("available_seats", 0)
        available_seats += avail
        if avail == 0:
            fully_booked_routes += 1

    occupied_seats = total_capacity - available_seats

    confirmed_bookings = 0
    cancelled_bookings = 0
    confirmed_revenue = 0
    reserved_seats = 0

    for booking in bookings:
        status = booking.get("status")
        if status == "Confirmed":
            confirmed_bookings += 1
            confirmed_revenue += booking.get("total_fare", 0)
            reserved_seats += booking.get("seats", 0)
        elif status == "Cancelled":
            cancelled_bookings += 1

    return {
        "total_routes": total_routes,
        "total_capacity": total_capacity,
        "available_seats": available_seats,
        "occupied_seats": occupied_seats,
        "total_bookings": len(bookings),
        "confirmed_bookings": confirmed_bookings,
        "cancelled_bookings": cancelled_bookings,
        "reserved_seats": reserved_seats,
        "confirmed_revenue": confirmed_revenue,
        "fully_booked_routes": fully_booked_routes
    }


def generate_report_text(
    routes: List[Dict[str, Any]],
    bookings: List[Dict[str, Any]]
) -> str:
    """
    Generate an exhaustive, beautifully formatted plain-text booking report.
    Demonstrates:
    - Summary metrics calculation
    - Exclusion of cancelled bookings from revenue and reserved seats
    - Nested loops: Outer loop scans routes, inner loop groups matching confirmed bookings
    - Clear handling of empty bookings state
    """
    metrics = calculate_dashboard_metrics(routes, bookings)

    lines: List[str] = [
        "=" * 60,
        "     SMART BUS TICKET BOOKING & RESERVATION SYSTEM",
        "                OFFICIAL BOOKING REPORT",
        "=" * 60,
        f"Total Bookings Created : {metrics['total_bookings']}",
        f"Confirmed Bookings     : {metrics['confirmed_bookings']}",
        f"Cancelled Bookings     : {metrics['cancelled_bookings']}",
        f"Seats Currently Reserved: {metrics['reserved_seats']}",
        f"Confirmed Revenue      : Rs. {metrics['confirmed_revenue']:,}",
        f"Fully Booked Routes    : {metrics['fully_booked_routes']}",
        "-" * 60,
        "CONFIRMED BOOKINGS GROUPED BY ROUTE:",
        "-" * 60
    ]

    # Nested loops: Outer loop visits each route, inner loop collects matching confirmed bookings
    for route in routes:
        r_id = route["route_id"]
        journey = f"{route['departure_city']} -> {route['destination_city']}"
        lines.append(f"\nRoute {r_id} ({journey}) | Fare: Rs. {route['ticket_price']:,} | Seats Remaining: {route['available_seats']}/{route['total_seats']}")

        matching_confirmed = []
        for booking in bookings:
            if booking.get("route_id") == r_id and booking.get("status") == "Confirmed":
                matching_confirmed.append(booking)

        if not matching_confirmed:
            lines.append("  * No active confirmed bookings on this route.")
        else:
            for idx, b in enumerate(matching_confirmed, start=1):
                lines.append(
                    f"  {idx}. [{b['booking_id']}] Passenger: {b['passenger_name']} (Age: {b['passenger_age']}) "
                    f"| Seats: {b['seats']} | Fare: Rs. {b['total_fare']:,}"
                )

    lines.append("\n" + "=" * 60)
    lines.append("           END OF REPORT — GENERATED IN SESSION")
    lines.append("=" * 60)

    return "\n".join(lines)


def sort_routes(
    routes: List[Dict[str, Any]],
    key_name: str = "route_id",
    reverse: bool = False
) -> List[Dict[str, Any]]:
    """
    Sort routes list demonstrating a Python lambda expression.
    """
    routes_copy = list(routes)
    routes_copy.sort(key=lambda r: r.get(key_name, 0), reverse=reverse)
    return routes_copy


def sort_bookings(
    bookings: List[Dict[str, Any]],
    key_name: str = "booking_id",
    reverse: bool = False
) -> List[Dict[str, Any]]:
    """
    Sort bookings list demonstrating a Python lambda expression.
    """
    bookings_copy = list(bookings)
    bookings_copy.sort(key=lambda b: b.get(key_name, ""), reverse=reverse)
    return bookings_copy
