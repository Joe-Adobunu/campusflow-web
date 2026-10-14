"""Tests for ticket creation, validation, and the priority engine."""

import unittest

from campusflow.tickets import (
    ValidationError,
    calculate_priority,
    create_ticket,
    next_ticket_id,
)


class TestPriorityEngine(unittest.TestCase):
    """The four §1.3 rules, applied first-match-wins."""

    def test_high_urgency_many_users_is_critical(self):
        # Rule 1: high AND >= 10 users -> critical
        self.assertEqual(calculate_priority("high", 12), "critical")

    def test_high_urgency_few_users_is_high(self):
        # Rule 2: high OR >= 10 -> high (falls here on high urgency)
        self.assertEqual(calculate_priority("high", 2), "high")

    def test_low_urgency_many_users_is_medium(self):
        # Rule 3: medium OR >= 3 -> medium (falls here on 4 users)
        self.assertEqual(calculate_priority("low", 4), "medium")

    def test_low_urgency_one_user_is_low(self):
        # Rule 4: nothing matched -> low
        self.assertEqual(calculate_priority("low", 1), "low")

    def test_boundary_high_urgency_10_users_is_critical(self):
        # §1.3 Rule 1 says "10 or more" -> the boundary itself is critical
        self.assertEqual(calculate_priority("high", 10), "critical")

    def test_boundary_9_users_high_urgency_is_high(self):
        # One user below the boundary -> Rule 2, not Rule 1
        self.assertEqual(calculate_priority("high", 9), "high")

    def test_boundary_3_users_low_urgency_is_medium(self):
        # §1.3 Rule 3 says "3 or more" -> the boundary itself is medium
        self.assertEqual(calculate_priority("low", 3), "medium")

    def test_boundary_10_users_medium_urgency_is_high(self):
        # Rule 2 fires before Rule 3 when users >= 10
        self.assertEqual(calculate_priority("medium", 10), "high")


class TestInputValidation(unittest.TestCase):
    """Every invalid input must be rejected, not silently accepted."""

    def test_zero_affected_users_rejected(self):
        with self.assertRaises(ValidationError):
            create_ticket([], "Test", "Network", "low", 0)

    def test_negative_affected_users_rejected(self):
        with self.assertRaises(ValidationError):
            create_ticket([], "Test", "Network", "low", -1)

    def test_decimal_affected_users_rejected(self):
        with self.assertRaises(ValidationError):
            create_ticket([], "Test", "Network", "low", 2.5)

    def test_text_affected_users_rejected(self):
        with self.assertRaises(ValidationError):
            create_ticket([], "Test", "Network", "low", "five")

    def test_boolean_affected_users_rejected(self):
        # True == 1 in Python; must be caught explicitly
        with self.assertRaises(ValidationError):
            create_ticket([], "Test", "Network", "low", True)

    def test_blank_title_rejected(self):
        with self.assertRaises(ValidationError):
            create_ticket([], "   ", "Network", "low", 1)

    def test_invalid_category_rejected(self):
        with self.assertRaises(ValidationError):
            create_ticket([], "Test", "banana", "low", 1)

    def test_invalid_urgency_rejected(self):
        with self.assertRaises(ValidationError):
            create_ticket([], "Test", "Network", "urgent", 1)


class TestCreation(unittest.TestCase):
    """The happy path and the ID generator."""

    def test_first_ticket_gets_T001_and_correct_defaults(self):
        tickets = []
        t = create_ticket(tickets, "Campus Wi-Fi down", "Network", "high", 15)
        self.assertEqual(t["id"], "T001")
        self.assertEqual(t["priority"], "critical")
        self.assertEqual(t["status"], "open")
        self.assertIsNone(t["assigned_to"])
        self.assertIn(t, tickets)

    def test_ids_increment_sequentially(self):
        tickets = []
        create_ticket(tickets, "A", "Network", "low", 1)
        create_ticket(tickets, "B", "Network", "low", 1)
        t3 = create_ticket(tickets, "C", "Network", "low", 1)
        self.assertEqual(t3["id"], "T003")

    def test_category_normalized_across_case_variants(self):
        # §1.2: "accept and normalize valid case variations consistently"
        for variant in ("NETWORK", "Network", "network", "  NeTwOrK  "):
            t = create_ticket([], "Wi-Fi", variant, "low", 1)
            self.assertEqual(t["category"], "Network", f"failed for {variant!r}")

    def test_urgency_normalized_across_case_variants(self):
        for variant in ("HIGH", "High", "high", "  HiGh  "):
            t = create_ticket([], "Wi-Fi", "Network", variant, 1)
            self.assertEqual(t["urgency"], "high", f"failed for {variant!r}")

    def test_ids_unique_after_simulated_reload(self):
        # Existing tickets on disk; new ticket must not collide with them.
        existing = [
            {"id": "T001", "title": "x", "category": "Network",
             "urgency": "low", "affected_users": 1, "priority": "low",
             "status": "open", "assigned_to": None},
            {"id": "T007", "title": "y", "category": "Network",
             "urgency": "low", "affected_users": 1, "priority": "low",
             "status": "open", "assigned_to": None},
        ]
        t = create_ticket(existing, "new", "Network", "low", 1)
        self.assertEqual(t["id"], "T008")

    def test_next_ticket_id_ignores_malformed_ids(self):
        # If a ticket id is malformed, we skip it, not crash.
        tickets = [{"id": "T003"}, {"id": "garbage"}, {"id": "T"}]
        self.assertEqual(next_ticket_id(tickets), "T004")


if __name__ == "__main__":
    unittest.main()
    