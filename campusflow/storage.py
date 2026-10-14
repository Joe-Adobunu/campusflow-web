"""JSON persistence. Only this module touches the filesystem."""

import json
import os


class StorageError(Exception):
    """Raised when the ticket store is unreadable or unwritable."""


REQUIRED_KEYS = {
    "id", "title", "category", "urgency",
    "affected_users", "priority", "status", "assigned_to",
}


def _validate_loaded_ticket(ticket, index):
    if not isinstance(ticket, dict):
        raise StorageError(f"Ticket at index {index} is not an object.")
    missing = REQUIRED_KEYS - ticket.keys()
    if missing:
        raise StorageError(
            f"Ticket at index {index} is missing fields: {sorted(missing)}."
        )


def load_tickets(path):
    """Return list of tickets.

    Missing file  -> []
    Corrupt JSON  -> StorageError (file is NOT overwritten)
    """
    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise StorageError(
            f"Ticket file {path} contains invalid JSON and was not loaded: {e}"
        ) from e
    except OSError as e:
        raise StorageError(f"Could not read {path}: {e}") from e

    if not isinstance(data, list):
        raise StorageError(f"Ticket file {path} must contain a JSON list.")

    for i, ticket in enumerate(data):
        _validate_loaded_ticket(ticket, i)

    return data


def save_tickets(tickets, path):
    """Write atomically: temp file, then os.replace."""
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)

    tmp = f"{path}.tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(tickets, f, indent=2)
        os.replace(tmp, path)
    except OSError as e:
        raise StorageError(f"Could not save tickets to {path}: {e}") from e
        