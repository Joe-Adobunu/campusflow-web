"""Tests for JSON persistence and corruption handling."""

import json
import os
import tempfile
import unittest

from campusflow.storage import StorageError, load_tickets, save_tickets


def sample_ticket(tid="T001"):
    return {
        "id": tid,
        "title": "Wi-Fi down",
        "category": "Network",
        "urgency": "high",
        "affected_users": 15,
        "priority": "critical",
        "status": "open",
        "assigned_to": None,
    }


class TestStorage(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "tickets.json")

    def tearDown(self):
        self.tmp.cleanup()

    def test_missing_file_returns_empty_list(self):
        # §1.4 F7: "Missing file should allow a fresh start"
        self.assertEqual(load_tickets(self.path), [])

    def test_save_then_load_round_trips(self):
        tickets = [sample_ticket("T001"), sample_ticket("T002")]
        save_tickets(tickets, self.path)
        self.assertEqual(load_tickets(self.path), tickets)

    def test_save_creates_parent_directory(self):
        nested = os.path.join(self.tmp.name, "data", "tickets.json")
        save_tickets([sample_ticket()], nested)
        self.assertTrue(os.path.exists(nested))

    def test_corrupted_json_raises_storage_error(self):
        # §1.4 F7: "malformed JSON should produce a clear error"
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("{ this is not json ]")
        with self.assertRaises(StorageError):
            load_tickets(self.path)

    def test_corrupted_file_is_not_overwritten_on_load(self):
        # §1.4 F7: "rather than silently erase data"
        original = "{ broken json"
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(original)
        with self.assertRaises(StorageError):
            load_tickets(self.path)
        with open(self.path, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), original)

    def test_non_list_json_raises(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({"oops": "not a list"}, f)
        with self.assertRaises(StorageError):
            load_tickets(self.path)

    def test_list_with_malformed_ticket_raises(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump([{"id": "T001"}], f)   # missing most fields
        with self.assertRaises(StorageError):
            load_tickets(self.path)

    def test_ids_remain_unique_after_reload(self):
        # §1.4 F7: "IDs must remain unique after reload"
        from campusflow.tickets import create_ticket
        save_tickets([sample_ticket("T005")], self.path)
        reloaded = load_tickets(self.path)
        new = create_ticket(reloaded, "new", "Network", "low", 1)
        self.assertEqual(new["id"], "T006")
        ids = [t["id"] for t in reloaded]
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()
    