"""Ticket totals and breakdowns."""

STATUSES = ["open", "in_progress", "resolved"]
PRIORITIES = ["critical", "high", "medium", "low"]


def _count_by(tickets, field, known_values):
    """Count tickets per value; anything unexpected lands in 'unknown'."""
    counts = {v: 0 for v in known_values}
    counts["unknown"] = 0
    for t in tickets:
        value = t.get(field)
        if value in counts and value != "unknown":
            counts[value] += 1
        else:
            counts["unknown"] += 1
    return counts


def generate_report(tickets):
    """Works correctly when `tickets` is empty."""
    return {
        "total": len(tickets),
        "by_status": _count_by(tickets, "status", STATUSES),
        "by_priority": _count_by(tickets, "priority", PRIORITIES),
    }


def print_report(tickets):
    report = generate_report(tickets)
    print("\n--- Ticket Report ---")
    print(f"Total tickets: {report['total']}")
    print("\nBy status:")
    for status, count in report["by_status"].items():
        print(f"  {status}: {count}")
    print("\nBy priority:")
    for priority, count in report["by_priority"].items():
        print(f"  {priority}: {count}")
        