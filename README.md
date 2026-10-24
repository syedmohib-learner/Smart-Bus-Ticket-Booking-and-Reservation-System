# 🚌 Smart Bus Ticket Booking & Reservation System

A hackathon and pair-programming project implementing a full-featured, interactive bus reservation management system in Python 3 and Streamlit.

---

## 1. Project Purpose & Problem Statement

Transportation operators face common operational challenges when managing bus routes manually or with disconnected systems:
- Overbooking coaches beyond their physical capacity.
- Seat count discrepancies between bookings and actual seat availability.
- Calculating revenue improperly by inadvertently including cancelled tickets.
- Double-restoring seats when an already-cancelled booking is processed a second time.
- Lack of centralized schedule visibility grouped by city.

The **Smart Bus Ticket Booking & Reservation System** solves these challenges by providing a reliable, interactive system designed with pure Python fundamentals and an intuitive Streamlit interface. It maintains exact seat counts, prevents double-restoration or negative capacities, excludes cancelled reservations from confirmed financial metrics, and organizes route schedules cleanly.

---

## 2. Main Features

- **📊 Dynamic Dashboard:** Live Key Performance Indicators (KPIs) showing total routes, total seat capacity, available seats, occupied seats, confirmed bookings, cancelled bookings, confirmed revenue in Pakistani Rupees (Rs.), and count of fully booked routes.
- **🚌 Route Catalog:** Comprehensive tabular view of all routes with departure times, fares, capacity, remaining seats, and dynamic status badges (`Available`, `Partially Booked`, `Fully Booked`). Includes a filter for routes with available seats and sorting by fare or available seats.
- **🔍 Intelligent Search:** Case-insensitive search across Route IDs, departure cities, and destination cities.
- **🎫 Validated Ticket Booking:** Streamlit form collecting passenger name, age, route selection, and seat count. Enforces all business rules (BR-01 to BR-08), generates unique sequential IDs (`B1001`, `B1002`, etc.), updates route availability, and provides confirmation summaries.
- **📋 Booking History:** Complete audit trail of all reservations (Confirmed and Cancelled) with status and route filters.
- **❌ Safe Cancellation Engine:** Cancels confirmed tickets, restores exact reserved seats to the coach capacity, prevents duplicate cancellations, and preserves records in history.
- **💺 Coach Seat Availability Tracker:** Real-time occupancy percentages, capacity trackers, and visual progress gauges for each bus.
- **📅 Departure City Schedules:** Route schedules systematically grouped by city of origin using nested loops and supported cities tuples.
- **📑 Downloadable Audit Reports:** Generates structured plain-text financial and operational reports with a single-click `.txt` download button.

---

## 3. Technologies Used

- **Programming Language:** Python 3 (Python 3.10+ / 3.14 compatible).
- **Web Interface:** Streamlit.
- **Data Tables:** Pandas (for displaying formatted Streamlit tables).
- **Core Storage:** Python in-memory data structures (`list`, `dict`, `tuple`, `set`) inside Streamlit session state (`st.session_state`).
- **Testing Framework:** Python's built-in `unittest` module.
- **Standard Library Modules:** `copy`, `typing`, `unittest`.

---

## 4. Project File Structure

```text
SMART BUS TICKET BOOKING & RESERVATION SYSTEM/
│
├── app.py                 # Streamlit web application & user interface
├── bus_functions.py       # Core business logic, validation, data models & helpers
├── test_app.py            # Automated test suite using Python unittest (22 test cases)
├── requirements.txt       # Project dependencies (streamlit, pandas)
├── README.md              # Project documentation, guides & concept walkthroughs
└── test_cases.txt         # Test scenarios, execution matrix & test outcomes
```

### Module Responsibilities:
- **`bus_functions.py`:** Decoupled business logic containing the starter route dataset, search functions, validation rules, booking logic, cancellation mechanics, schedule builders, and report calculations. No UI dependencies, making it directly testable.
- **`app.py`:** The Streamlit user interface coordinating navigation, input forms, data visualizations, metrics cards, tables, alerts, and file download triggers.
- **`test_app.py`:** Independent automated test suite verifying 100% of the PRD business logic and boundary rules without needing a browser.
- **`test_cases.txt`:** Formal test execution log recording scenarios, inputs, expected outcomes, and actual results.

---

## 5. Initial Starter Route Data

The system initializes with five fictional inter-city bus routes:

| Route ID | Departure City | Destination City | Departure Time | Fare per Seat | Total Capacity | Available Seats |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **R101** | Karachi | Hyderabad | 08:00 AM | Rs. 1,200 | 40 | 40 |
| **R102** | Karachi | Sukkur | 09:30 AM | Rs. 2,000 | 36 | 36 |
| **R103** | Hyderabad | Mirpur Khas | 11:00 AM | Rs. 800 | 32 | 32 |
| **R104** | Karachi | Lahore | 07:00 PM | Rs. 5,000 | 45 | 45 |
| **R105** | Sukkur | Hyderabad | 02:00 PM | Rs. 1,500 | 30 | 30 |

Supported cities tuple: `('Karachi', 'Hyderabad', 'Sukkur', 'Mirpur Khas', 'Lahore')`.

---

## 6. Installation Instructions

Ensure you have Python 3 installed. Open a terminal or PowerShell in the project directory:

```bash
# Optional: create and activate a virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

---

## 7. How to Run the Application

Run the Streamlit application with the following command:

```bash
streamlit run app.py
```

The application will start and automatically open in your default web browser (typically at `http://localhost:8501`).

---

## 8. Feature Walkthrough & Usage Guide

### 8.1 📊 Dashboard
- View high-level metrics for routes, seat capacity, confirmed reservations, and confirmed revenue.
- Inspect the live overview table of all routes with color-coded status badges.

### 8.2 🚌 View Available Routes
- Browse the route catalog.
- Check "Show only routes with available seats" to filter out fully booked coaches.
- Use the sort dropdown to order routes by Lowest Fare, Highest Fare, Most Available Seats, or Route ID.

### 8.3 🔍 Search Routes
- Enter an exact Route ID (`R101`) or a city name (`Karachi`, `Hyderabad`, `sukkur`).
- Search is case-insensitive and trims unnecessary whitespace.
- View matching routes or receive an informative notification if no matching route exists.

### 8.4 🎫 Book a Ticket
- Fill in the passenger name and age.
- Choose a route from the dropdown menu (which displays journey details, fare, and remaining seats).
- Select the number of seats. The system displays a live fare estimate.
- Click **Confirm Reservation**. If validation passes:
  - A unique booking ID is assigned (e.g. `B1001`).
  - Available seats on the chosen route are decremented immediately.
  - A confirmation card appears with full trip details.

### 8.5 📋 View My Bookings
- View all reservations created during your session.
- Filter records by status (`Confirmed` or `Cancelled`) and by Route ID.
- Displays passenger names, ages, journeys, seat quantities, and fares paid.

### 8.6 ❌ Cancel a Booking
- Select any active booking from the dropdown of confirmed reservations or type in a Booking ID manually.
- Click **Cancel Reservation**.
- The system verifies the booking is `Confirmed`, restores the reserved seats to the route, and updates the status to `Cancelled`.
- Attempting to cancel an already-cancelled booking is safely blocked.

### 8.7 💺 View Seat Availability
- Examine coach capacity, occupied seats (`total_seats - available_seats`), remaining seats, and occupancy percentages.
- View visual progress bars for each bus route.

### 8.8 📅 Route Schedules
- View schedules organized by departure city.
- Cities without departing routes (such as Mirpur Khas and Lahore in initial data) display `No scheduled departures.`

### 8.9 📑 Booking Reports
- Review an operational report summarizing totals, confirmed seats, revenue, and route-by-route reservations.
- Click **Download Official Report (.txt)** to save a plain-text report directly to your computer.

---

## 9. Python Concepts Used in the Code

This project demonstrates core Python fundamentals:

1. **Variables & Data Types:**
   - Integers for seat counts, passenger ages, and rupee values.
   - Strings for names, route IDs, cities, timestamps, and status flags.
   - Booleans for validation results and conditional filters.

2. **Core Data Structures:**
   - **Lists:** Ordered sequences storing routes (`routes = [...]`) and booking records (`bookings = [...]`).
   - **Dictionaries:** Key-value mappings representing individual route specifications and booking records.
   - **Tuples:** Immutable collection `SUPPORTED_CITIES = ('Karachi', 'Hyderabad', 'Sukkur', 'Mirpur Khas', 'Lahore')` safeguarding standard city names from accidental runtime modification.
   - **Sets:** Unordered collection `issued_ids = {'B1001', ...}` providing $O(1)$ constant-time lookup to prevent duplicate booking identifiers.

3. **Conditional Control Flow (`if`, `elif`, `else`):**
   - Classifying route statuses (`Available`, `Partially Booked`, `Fully Booked`).
   - Checking input boundary conditions (non-blank strings, positive integers, remaining seat limits).

4. **Loops and Iterations:**
   - **`for` loops:** Traversing route listings, booking records, and city lists.
   - **Nested `for` loops:**
     - Building city schedules (outer loop over `SUPPORTED_CITIES`, inner loop over `routes`).
     - Generating reports (outer loop over `routes`, inner loop over `bookings` matching the route ID).
   - **`enumerate()`:** Numbering table records cleanly starting at 1.
   - **`break`:** Halting search loops once a unique Route ID or Booking ID match is located.
   - **`continue`:** Skipping fully booked routes when the available-only filter is enabled.
   - **`for-else`:** Handling "not found" scenarios when a loop completes without executing a `break`.
   - **`while` loops:** Generating sequential unique booking IDs until an unused ID is found in the set.

5. **Lambda Functions:**
   - Used for lightweight, readable list sorting (e.g. `routes.sort(key=lambda r: r['ticket_price'])`).

6. **Exception Handling (`try` / `except`):**
   - Safely converting text input to integers for passenger age and seat count, catching `ValueError` and `TypeError` gracefully without crashing.

7. **File Handling:**
   - Formatting and producing downloadable plain-text reports using string composition and Streamlit's buffer handlers.

---

## 10. Booking Validation & Seat Updates

Before any seat count changes or booking records are created, `validate_booking_inputs()` enforces five business rules:

1. **BR-01 (Passenger Name):** Must be a string with non-whitespace characters.
2. **BR-02 (Passenger Age):** Must convert to a positive integer ($> 0$).
3. **BR-03 (Route Existence):** Route ID must exist in the active route list.
4. **BR-04 (Seat Quantity):** Requested seats must be a positive integer ($> 0$).
5. **BR-05 (Seat Availability):** Requested seats must be $\le$ the route's current `available_seats`.

Only when all rules pass:
- Total fare is computed: `total_fare = route["ticket_price"] * seats`.
- Available seats are decremented exactly once: `route["available_seats"] -= seats`.
- A new booking record is appended to the bookings list.

---

## 11. Cancellation Mechanics & Financial Reports

### Cancellation Integrity:
- When a cancellation is requested, `cancel_booking()` searches the bookings list.
- If the booking status is `Cancelled`, the request is rejected with a clear message: `"Booking is already cancelled. Seats cannot be restored again."`
- If confirmed, reserved seats are added back to the route's available seats, ensuring `available_seats <= total_seats`.
- The booking status is changed to `Cancelled`, and the record remains in booking history.

### Financial Reporting Logic:
- **Total Bookings:** Counts every booking record (Confirmed + Cancelled).
- **Confirmed Bookings:** Counts only bookings where `status == "Confirmed"`.
- **Cancelled Bookings:** Counts bookings where `status == "Cancelled"`.
- **Reserved Seats:** Sum of `seats` for confirmed bookings only.
- **Confirmed Revenue:** Sum of `total_fare` for confirmed bookings only. **Cancelled bookings are strictly excluded from confirmed revenue.**
- **Empty State:** When no bookings exist, booking counts and revenue evaluate cleanly to 0, while route capacity is still accurately computed.

---

## 12. Automated Testing Instructions

The project includes an automated test suite written using Python's built-in `unittest` framework in `test_app.py`.

To run the unit tests:

```bash
python -m unittest test_app.py -v
```

### Test Coverage Highlights (22 Unit Tests):
- Route catalog initialization (all 5 routes loaded with full seats).
- Route searching by ID and city, including case-insensitive handling.
- Unknown search queries returning empty lists.
- Fare calculations and unique booking ID issuance.
- Rejection of blank names, non-numeric ages, zero or negative seats, and overbooking.
- Successful cancellation and seat restoration.
- Prevention of double-cancellation and double-restoration.
- Retention of cancelled bookings in history.
- Exclusion of cancelled fares from revenue metrics.
- Report generation with empty and populated states.
- Departure city schedule nesting and city coverage.

---

## 13. System Limitations

- **Session-Only In-Memory Storage:** Route data, bookings, and seat adjustments are stored in Streamlit session state (`st.session_state`). When the user closes the session or the server restarts, data resets to default starter values. This complies with the hackathon specification of using pure Python data structures without external databases.
- **Single-User Simulation:** The application runs as a local reservation simulation; concurrent multi-user database transactions are intentionally out of scope.

---

## 14. Possible Future Improvements

- Add persistent database storage (SQLite / PostgreSQL) to retain bookings across server restarts.
- Add passenger ticket PDF generation with QR codes.
- Implement specific seat number selection (e.g. 1A, 1B, 2A).
- Add SMS / Email booking confirmations.
- Support multi-leg connecting journeys.
