"""Tests for assignment, status workflow, and the work queue."""

import unittest

from campusflow.tickets import create_ticket
from campusflow.workflow import (
    WorkflowError,
    assign_ticket,
    find_ticket,
    get_work_queue,
    reopen_ticket,
    update_status,
)


def make_tickets():
    """A small fixture with a mix of priorities and statuses."""
    tickets = []
    create_ticket(tickets, "Wi-Fi down", "Network", "high", 12)     # T001 critical
    create_ticket(tickets, "Printer jam", "Hardware", "low", 1)     # T002 low
    create_ticket(tickets, "VPN issue", "Network", "medium", 5)     # T003 medium
    create_ticket(tickets, "Laptop crash", "Hardware", "high", 2)   # T004 high
    return tickets


class TestFindAndAssign(unittest.TestCase):
    def test_find_unknown_ticket_raises(self):
        with self.assertRaises(WorkflowError):
            find_ticket(make_tickets(), "T999")

    def test_assign_sets_assigned_to(self):
        tickets = make_tickets()
        t = assign_ticket(tickets, "T001", "Amina")
        self.assertEqual(t["assigned_to"], "Amina")

    def test_assign_blank_name_rejected(self):
        with self.assertRaises(WorkflowError):
            assign_ticket(make_tickets(), "T001", "   ")

    def test_assign_unknown_ticket_rejected(self):
        with self.assertRaises(WorkflowError):
            assign_ticket(make_tickets(), "T999", "Amina")


class TestStatusTransitions(unittest.TestCase):
    def test_unassigned_cannot_start(self):
        # §1.4 F4: "Do not move an unassigned ticket into in_progress"
        with self.assertRaises(WorkflowError):
            update_status(make_tickets(), "T001", "in_progress")

    def test_assigned_can_start_and_resolve(self):
        # Full happy-path cycle: assign -> start -> resolve
        tickets = make_tickets()
        assign_ticket(tickets, "T001", "Amina")
        update_status(tickets, "T001", "in_progress")
        update_status(tickets, "T001", "resolved")
        self.assertEqual(tickets[0]["status"], "resolved")

    def test_open_cannot_jump_to_resolved(self):
        # Must pass through in_progress first.
        tickets = make_tickets()
        assign_ticket(tickets, "T001", "Amina")
        with self.assertRaises(WorkflowError):
            update_status(tickets, "T001", "resolved")

    def test_invalid_status_value_rejected(self):
        with self.assertRaises(WorkflowError):
            update_status(make_tickets(), "T001", "finished")

    def test_in_progress_cannot_go_back_to_open(self):
        tickets = make_tickets()
        assign_ticket(tickets, "T001", "Amina")
        update_status(tickets, "T001", "in_progress")
        with self.assertRaises(WorkflowError):
            update_status(tickets, "T001", "open")

    def test_resolved_is_locked_until_reopened(self):
        tickets = make_tickets()
        assign_ticket(tickets, "T001", "Amina")
        update_status(tickets, "T001", "in_progress")
        update_status(tickets, "T001", "resolved")
        with self.assertRaises(WorkflowError):
            update_status(tickets, "T001", "in_progress")

    def test_reopen_sets_status_open(self):
        tickets = make_tickets()
        assign_ticket(tickets, "T001", "Amina")
        update_status(tickets, "T001", "in_progress")
        update_status(tickets, "T001", "resolved")
        reopen_ticket(tickets, "T001")
        self.assertEqual(tickets[0]["status"], "open")

    def test_reopen_non_resolved_ticket_rejected(self):
        with self.assertRaises(WorkflowError):
            reopen_ticket(make_tickets(), "T001")


class TestWorkQueue(unittest.TestCase):
    def test_queue_excludes_resolved(self):
        tickets = make_tickets()
        assign_ticket(tickets, "T001", "Amina")
        update_status(tickets, "T001", "in_progress")
        update_status(tickets, "T001", "resolved")
        queue_ids = [t["id"] for t in get_work_queue(tickets)]
        self.assertNotIn("T001", queue_ids)

    def test_queue_sorted_by_priority_then_id(self):
        tickets = make_tickets()
        # Sort order should be: T001 (critical), T004 (high),
        # T003 (medium), T002 (low)
        queue_ids = [t["id"] for t in get_work_queue(tickets)]
        self.assertEqual(queue_ids, ["T001", "T004", "T003", "T002"])

    def test_queue_breaks_priority_ties_by_numeric_id(self):
        # Two medium tickets; T005 and T010 must sort as 5 then 10, not
        # lexicographically ("T010" < "T005" alphabetically).
        tickets = []
        create_ticket(tickets, "A", "Network", "medium", 3)   # T001 medium
        create_ticket(tickets, "B", "Network", "medium", 3)   # T002 medium
        create_ticket(tickets, "C", "Network", "medium", 3)   # T003 medium
        # fast-forward ids
        tickets.extend([
            {"id": "T005", "title": "D", "category": "Network",
             "urgency": "medium", "affected_users": 3, "priority": "medium",
             "status": "open", "assigned_to": None},
            {"id": "T010", "title": "E", "category": "Network",
             "urgency": "medium", "affected_users": 3, "priority": "medium",
             "status": "open", "assigned_to": None},
        ])
        queue_ids = [t["id"] for t in get_work_queue(tickets)]
        self.assertLess(queue_ids.index("T005"), queue_ids.index("T010"))


if __name__ == "__main__":
    unittest.main()
    