"""
Unit Test Suite for Smart Bus Ticket Booking & Reservation System
Using Python's built-in unittest framework.
"""

import unittest
from bus_functions import (
    SUPPORTED_CITIES,
    DEFAULT_ROUTES,
    get_initial_routes,
    get_route_status,
    calculate_occupied_seats,
    find_route_by_id,
    search_routes,
    filter_available_routes,
    generate_booking_id,
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


class TestSmartBusBookingSystem(unittest.TestCase):

    def setUp(self):
        """Prepare fresh routes, empty bookings, and fresh issued_ids for each test."""
        self.routes = get_initial_routes()
        self.bookings = []
        self.issued_ids = set()

    # 1. All five routes initialize correctly
    def test_01_routes_initialization(self):
        self.assertEqual(len(self.routes), 5)
        expected_ids = ["R101", "R102", "R103", "R104", "R105"]
        actual_ids = [r["route_id"] for r in self.routes]
        self.assertEqual(actual_ids, expected_ids)
        for route in self.routes:
            self.assertEqual(route["available_seats"], route["total_seats"])
            self.assertEqual(get_route_status(route), "Available")
            self.assertGreater(route["ticket_price"], 0)

    # 2. Route search finds matching routes
    def test_02_route_search_matching(self):
        # Search by exact route ID
        res_id = search_routes(self.routes, "R101")
        self.assertEqual(len(res_id), 1)
        self.assertEqual(res_id[0]["route_id"], "R101")

        # Search by city 'Hyderabad' (departures or destinations)
        res_city = search_routes(self.routes, "Hyderabad")
        # R101 (Karachi -> Hyderabad), R103 (Hyderabad -> Mirpur Khas), R105 (Sukkur -> Hyderabad)
        self.assertEqual(len(res_city), 3)

        # Case-insensitive and trimmed search
        res_lower = search_routes(self.routes, "   karachi  ")
        # R101, R102, R104
        self.assertEqual(len(res_lower), 3)

    # 3. Searching for an unknown city returns no matches
    def test_03_route_search_unknown_city(self):
        results = search_routes(self.routes, "Atlantis")
        self.assertEqual(results, [])
        self.assertEqual(len(results), 0)

    # 4. A valid booking creates a unique ID
    def test_04_valid_booking_creates_unique_id(self):
        success1, b1 = book_ticket(
            self.routes, self.bookings, self.issued_ids,
            passenger_name="Ahmed", passenger_age=25, route_id="R101", seat_count=2
        )
        self.assertTrue(success1)
        self.assertEqual(b1["booking_id"], "B1001")
        self.assertIn("B1001", self.issued_ids)

        success2, b2 = book_ticket(
            self.routes, self.bookings, self.issued_ids,
            passenger_name="Sara", passenger_age=30, route_id="R102", seat_count=1
        )
        self.assertTrue(success2)
        self.assertEqual(b2["booking_id"], "B1002")
        self.assertNotEqual(b1["booking_id"], b2["booking_id"])

    # 5. Booking two seats on R101 calculates Rs. 2,400 correctly
    def test_05_fare_calculation(self):
        # Fare for R101 is 1,200 * 2 = 2,400
        success, booking = book_ticket(
            self.routes, self.bookings, self.issued_ids,
            passenger_name="Ahmed", passenger_age=24, route_id="R101", seat_count=2
        )
        self.assertTrue(success)
        self.assertEqual(booking["fare_per_seat"], 1200)
        self.assertEqual(booking["seats"], 2)
        self.assertEqual(booking["total_fare"], 2400)

    # 6. Booking reduces available seats by the correct amount
    def test_06_booking_reduces_available_seats(self):
        r101 = find_route_by_id(self.routes, "R101")
        self.assertEqual(r101["available_seats"], 40)

        book_ticket(
            self.routes, self.bookings, self.issued_ids,
            passenger_name="Ahmed", passenger_age=24, route_id="R101", seat_count=3
        )
        self.assertEqual(r101["available_seats"], 37)
        self.assertEqual(calculate_occupied_seats(r101), 3)
        self.assertEqual(get_route_status(r101), "Partially Booked")

    # 7. An empty passenger name is rejected
    def test_07_empty_passenger_name_rejected(self):
        success, err = book_ticket(
            self.routes, self.bookings, self.issued_ids,
            passenger_name="   ", passenger_age=24, route_id="R101", seat_count=2
        )
        self.assertFalse(success)
        self.assertIn("Passenger name cannot be empty", err)
        self.assertEqual(len(self.bookings), 0)

    # 8. An invalid age is rejected
    def test_08_invalid_age_rejected(self):
        # Zero age
        s1, e1 = book_ticket(self.routes, self.bookings, self.issued_ids, "Bilal", 0, "R101", 1)
        self.assertFalse(s1)

        # Negative age
        s2, e2 = book_ticket(self.routes, self.bookings, self.issued_ids, "Bilal", -5, "R101", 1)
        self.assertFalse(s2)

        # Non-numeric text
        s3, e3 = book_ticket(self.routes, self.bookings, self.issued_ids, "Bilal", "twenty", "R101", 1)
        self.assertFalse(s3)

        self.assertEqual(len(self.bookings), 0)

    # 9. Zero or negative seat quantities are rejected
    def test_09_invalid_seat_quantity_rejected(self):
        s_zero, e_zero = book_ticket(self.routes, self.bookings, self.issued_ids, "Bilal", 25, "R101", 0)
        self.assertFalse(s_zero)

        s_neg, e_neg = book_ticket(self.routes, self.bookings, self.issued_ids, "Bilal", 25, "R101", -2)
        self.assertFalse(s_neg)

        s_str, e_str = book_ticket(self.routes, self.bookings, self.issued_ids, "Bilal", 25, "R101", "abc")
        self.assertFalse(s_str)

        self.assertEqual(len(self.bookings), 0)

    # 10. Booking more seats than available is rejected
    def test_10_overbooking_rejected(self):
        r101 = find_route_by_id(self.routes, "R101")
        # R101 has 40 seats
        success, err = book_ticket(
            self.routes, self.bookings, self.issued_ids,
            "Bilal", 25, "R101", 41
        )
        self.assertFalse(success)
        self.assertIn("only has 40 seat(s) available", err)
        self.assertEqual(r101["available_seats"], 40)
        self.assertEqual(len(self.bookings), 0)

    # 11. An unknown route is rejected
    def test_11_unknown_route_rejected(self):
        success, err = book_ticket(
            self.routes, self.bookings, self.issued_ids,
            "Bilal", 25, "R999", 2
        )
        self.assertFalse(success)
        self.assertIn("does not exist", err)
        self.assertEqual(len(self.bookings), 0)

    # 12. A confirmed booking can be cancelled
    def test_12_confirmed_booking_can_be_cancelled(self):
        book_ticket(self.routes, self.bookings, self.issued_ids, "Ahmed", 24, "R101", 2)
        self.assertEqual(self.bookings[0]["status"], "Confirmed")

        success, details = cancel_booking(self.routes, self.bookings, "B1001")
        self.assertTrue(success)
        self.assertEqual(self.bookings[0]["status"], "Cancelled")
        self.assertEqual(details["seats_restored"], 2)

    # 13. Cancellation restores the correct number of seats
    def test_13_cancellation_restores_seats(self):
        r101 = find_route_by_id(self.routes, "R101")
        self.assertEqual(r101["available_seats"], 40)

        book_ticket(self.routes, self.bookings, self.issued_ids, "Ahmed", 24, "R101", 5)
        self.assertEqual(r101["available_seats"], 35)

        success, _ = cancel_booking(self.routes, self.bookings, "B1001")
        self.assertTrue(success)
        self.assertEqual(r101["available_seats"], 40)

    # 14. Cancelling the same booking twice does not restore seats twice
    def test_14_cannot_cancel_same_booking_twice(self):
        r101 = find_route_by_id(self.routes, "R101")
        book_ticket(self.routes, self.bookings, self.issued_ids, "Ahmed", 24, "R101", 4)
        self.assertEqual(r101["available_seats"], 36)

        # First cancellation
        s1, _ = cancel_booking(self.routes, self.bookings, "B1001")
        self.assertTrue(s1)
        self.assertEqual(r101["available_seats"], 40)

        # Second cancellation attempt
        s2, err2 = cancel_booking(self.routes, self.bookings, "B1001")
        self.assertFalse(s2)
        self.assertIn("already cancelled", err2)
        # Seats should not exceed capacity
        self.assertEqual(r101["available_seats"], 40)

    # 15. Cancelled records remain in booking history
    def test_15_cancelled_records_remain_in_history(self):
        book_ticket(self.routes, self.bookings, self.issued_ids, "Ahmed", 24, "R101", 2)
        cancel_booking(self.routes, self.bookings, "B1001")
        self.assertEqual(len(self.bookings), 1)
        self.assertEqual(self.bookings[0]["booking_id"], "B1001")
        self.assertEqual(self.bookings[0]["status"], "Cancelled")

    # 16. Cancelled fares are excluded from confirmed revenue
    def test_16_revenue_excludes_cancelled_fares(self):
        # Booking 1: R101 (2 * 1200 = 2400)
        book_ticket(self.routes, self.bookings, self.issued_ids, "Ahmed", 24, "R101", 2)
        # Booking 2: R102 (1 * 2000 = 2000)
        book_ticket(self.routes, self.bookings, self.issued_ids, "Sara", 30, "R102", 1)

        metrics1 = calculate_dashboard_metrics(self.routes, self.bookings)
        self.assertEqual(metrics1["confirmed_revenue"], 4400)
        self.assertEqual(metrics1["confirmed_bookings"], 2)
        self.assertEqual(metrics1["cancelled_bookings"], 0)

        # Cancel Booking 1 (Rs. 2400)
        cancel_booking(self.routes, self.bookings, "B1001")

        metrics2 = calculate_dashboard_metrics(self.routes, self.bookings)
        self.assertEqual(metrics2["confirmed_revenue"], 2000)
        self.assertEqual(metrics2["confirmed_bookings"], 1)
        self.assertEqual(metrics2["cancelled_bookings"], 1)
        self.assertEqual(metrics2["reserved_seats"], 1)

    # 17. An empty booking list produces zero booking totals and revenue
    def test_17_empty_bookings_zero_metrics(self):
        metrics = calculate_dashboard_metrics(self.routes, [])
        self.assertEqual(metrics["total_bookings"], 0)
        self.assertEqual(metrics["confirmed_bookings"], 0)
        self.assertEqual(metrics["cancelled_bookings"], 0)
        self.assertEqual(metrics["reserved_seats"], 0)
        self.assertEqual(metrics["confirmed_revenue"], 0)
        self.assertEqual(metrics["fully_booked_routes"], 0)
        self.assertEqual(metrics["total_routes"], 5)

    # 18. Fully booked routes are counted correctly
    def test_18_fully_booked_routes_counted(self):
        r105 = find_route_by_id(self.routes, "R105")
        # R105 has 30 seats
        success, _ = book_ticket(self.routes, self.bookings, self.issued_ids, "Group Leader", 40, "R105", 30)
        self.assertTrue(success)
        self.assertEqual(r105["available_seats"], 0)
        self.assertEqual(get_route_status(r105), "Fully Booked")

        metrics = calculate_dashboard_metrics(self.routes, self.bookings)
        self.assertEqual(metrics["fully_booked_routes"], 1)

    # 19. Route availability never becomes negative or exceeds capacity
    def test_19_availability_boundaries(self):
        r103 = find_route_by_id(self.routes, "R103")
        total = r103["total_seats"]

        # Attempt to over-restore directly
        r103["available_seats"] = total
        # Cancelling a fake scenario won't push beyond total_seats
        success, _ = book_ticket(self.routes, self.bookings, self.issued_ids, "Passenger", 20, "R103", 32)
        self.assertEqual(r103["available_seats"], 0)
        cancel_booking(self.routes, self.bookings, "B1001")
        self.assertLessEqual(r103["available_seats"], total)
        self.assertGreaterEqual(r103["available_seats"], 0)

    # 20. Route schedules grouping by departure city
    def test_20_route_schedules_structure(self):
        schedules = get_route_schedules(self.routes, SUPPORTED_CITIES)
        for city in SUPPORTED_CITIES:
            self.assertIn(city, schedules)

        # Karachi should have 3 departing routes: R101, R102, R104
        self.assertEqual(len(schedules["Karachi"]), 3)
        # Mirpur Khas and Lahore have 0 departures
        self.assertEqual(len(schedules["Mirpur Khas"]), 0)
        self.assertEqual(len(schedules["Lahore"]), 0)

    # 21. Filter available routes
    def test_21_filter_available_routes(self):
        # Book all seats of R105
        book_ticket(self.routes, self.bookings, self.issued_ids, "Test", 25, "R105", 30)
        filtered = filter_available_routes(self.routes)
        self.assertEqual(len(filtered), 4)
        for r in filtered:
            self.assertGreater(r["available_seats"], 0)

    # 22. Report text generation
    def test_22_generate_report_text(self):
        book_ticket(self.routes, self.bookings, self.issued_ids, "Ahmed", 24, "R101", 2)
        text = generate_report_text(self.routes, self.bookings)
        self.assertIn("OFFICIAL BOOKING REPORT", text)
        self.assertIn("Total Bookings Created : 1", text)
        self.assertIn("Confirmed Revenue      : Rs. 2,400", text)
        self.assertIn("Ahmed", text)


if __name__ == "__main__":
    unittest.main()
