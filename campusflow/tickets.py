"""Ticket creation, validation, and the priority engine."""

CATEGORIES = ("Network", "Hardware", "Software", "Other")
URGENCIES = ("low", "medium", "high")


class ValidationError(ValueError):
    """Raised when ticket input is invalid."""


def normalize_category(value):
    """Accept 'network', 'NETWORK', '  Network  ' and return 'Network'."""
    if not isinstance(value, str):
        raise ValidationError("Category must be text.")
    cleaned = value.strip().lower()
    for c in CATEGORIES:
        if c.lower() == cleaned:
            return c
    raise ValidationError(
        f"Category must be one of: {', '.join(CATEGORIES)}."
    )


def normalize_urgency(value):
    """Accept 'High', 'HIGH', 'high' and return 'high'."""
    if not isinstance(value, str):
        raise ValidationError("Urgency must be text.")
    cleaned = value.strip().lower()
    if cleaned not in URGENCIES:
        raise ValidationError(
            f"Urgency must be one of: {', '.join(URGENCIES)}."
        )
    return cleaned


def validate_title(value):
    if not isinstance(value, str) or not value.strip():
        raise ValidationError("Title must not be blank.")
    return value.strip()


def validate_affected_users(value):
    # bool is a subclass of int in Python, so True/False would sneak through.
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError("affected_users must be a whole number.")
    if value <= 0:
        raise ValidationError("affected_users must be greater than zero.")
    return value


def calculate_priority(urgency, affected_users):
    """Apply the four rules in order; return the first match.

    Rule 1: high AND >= 10  -> critical
    Rule 2: high OR  >= 10  -> high
    Rule 3: medium OR >= 3  -> medium
    Rule 4: everything else -> low
    """
    urgency = normalize_urgency(urgency)
    affected_users = validate_affected_users(affected_users)

    if urgency == "high" and affected_users >= 10:
        return "critical"
    if urgency == "high" or affected_users >= 10:
        return "high"
    if urgency == "medium" or affected_users >= 3:
        return "medium"
    return "low"


def next_ticket_id(tickets):
    """Return T001, T002, ... based on the highest ID currently present.

    Scanning the list (instead of a counter) keeps IDs unique after a reload.
    """
    highest = 0
    for ticket in tickets:
        raw = ticket.get("id", "")
        if not isinstance(raw, str) or len(raw) < 2 or not raw[1:].isdigit():
            continue
        number = int(raw[1:])
        if number > highest:
            highest = number
    return f"T{highest + 1:03d}"


def create_ticket(tickets, title, category, urgency, affected_users):
    """Validate inputs, build a ticket dict, append to `tickets`, return it."""
    ticket = {
        "id": next_ticket_id(tickets),
        "title": validate_title(title),
        "category": normalize_category(category),
        "urgency": normalize_urgency(urgency),
        "affected_users": validate_affected_users(affected_users),
        "priority": calculate_priority(urgency, affected_users),
        "status": "open",
        "assigned_to": None,
    }
    tickets.append(ticket)
    return ticket
    