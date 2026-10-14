"""Assignment, status transitions, and the work queue."""


class WorkflowError(ValueError):
    """Raised when a workflow action is not allowed."""


PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}

# Only these transitions are legal. Everything else is rejected.
ALLOWED_TRANSITIONS = {
    "open": {"in_progress"},
    "in_progress": {"resolved"},
    "resolved": set(),   # only reopen_ticket() can unlock
}


def find_ticket(tickets, ticket_id):
    for ticket in tickets:
        if ticket.get("id") == ticket_id:
            return ticket
    raise WorkflowError(f"Ticket {ticket_id} was not found.")


def assign_ticket(tickets, ticket_id, staff_name):
    ticket = find_ticket(tickets, ticket_id)
    if not isinstance(staff_name, str) or not staff_name.strip():
        raise WorkflowError("Staff name must not be blank.")
    if ticket["status"] == "resolved":
        raise WorkflowError("Reopen the ticket before modifying it.")
    ticket["assigned_to"] = staff_name.strip()
    return ticket


def update_status(tickets, ticket_id, new_status):
    ticket = find_ticket(tickets, ticket_id)

    if not isinstance(new_status, str):
        raise WorkflowError("Status must be text.")
    new_status = new_status.strip().lower()

    if new_status not in {"open", "in_progress", "resolved"}:
        raise WorkflowError("Status must be open, in_progress, or resolved.")

    current = ticket["status"]

    if current == "resolved":
        raise WorkflowError("Reopen the ticket before changing its status.")

    if new_status not in ALLOWED_TRANSITIONS[current]:
        raise WorkflowError(
            f"Cannot move from {current} to {new_status}. "
            f"Allowed from {current}: {sorted(ALLOWED_TRANSITIONS[current]) or 'none'}."
        )

    if current == "open" and new_status == "in_progress" and not ticket["assigned_to"]:
        raise WorkflowError("Assign the ticket before starting work.")

    ticket["status"] = new_status
    return ticket


def reopen_ticket(tickets, ticket_id):
    ticket = find_ticket(tickets, ticket_id)
    if ticket["status"] != "resolved":
        raise WorkflowError("Only resolved tickets can be reopened.")
    ticket["status"] = "open"
    return ticket


def get_work_queue(tickets):
    """Unresolved tickets, critical first, ties broken by numeric ID."""
    unresolved = [t for t in tickets if t["status"] != "resolved"]
    return sorted(
        unresolved,
        key=lambda t: (PRIORITY_ORDER[t["priority"]], int(t["id"][1:])),
    )
    