"""CampusFlow command-line interface.

Only this file uses input() and print(). All business logic lives in
campusflow/*.py so it can be unit-tested without a terminal.
"""

import os
import sys

from campusflow import reports, storage, tickets, workflow

DATA_FILE = os.path.join("data", "tickets.json")


def prompt(text):
    return input(text).strip()


def pause():
    input("\nPress Enter to continue...")


def do_create(tickets_list):
    print("\n--- Create ticket ---")
    try:
        title = prompt("Title: ")
        category = prompt("Category (Network/Hardware/Software/Other): ")
        urgency = prompt("Urgency (low/medium/high): ")
        users_raw = prompt("Affected users: ")

        try:
            affected_users = int(users_raw)
        except ValueError:
            raise tickets.ValidationError("Affected users must be a whole number.")

        ticket = tickets.create_ticket(
            tickets_list, title, category, urgency, affected_users
        )
        print(
            f"Created {ticket['id']}: {ticket['title']} "
            f"[{ticket['priority']}]"
        )
    except tickets.ValidationError as e:
        print(f"Error: {e}")


def do_list(tickets_list):
    print("\n--- All tickets ---")
    if not tickets_list:
        print("No tickets yet.")
        return
    for t in tickets_list:
        assignee = t["assigned_to"] or "unassigned"
        print(
            f"{t['id']} | {t['title']} | {t['category']} | "
            f"{t['priority']} | {t['status']} | {assignee}"
        )


def do_view(tickets_list):
    ticket_id = prompt("Ticket ID (e.g. T001): ")
    try:
        t = workflow.find_ticket(tickets_list, ticket_id)
    except workflow.WorkflowError as e:
        print(f"Error: {e}")
        return
    print("\n--- Ticket details ---")
    for key in ("id", "title", "category", "urgency", "affected_users",
                "priority", "status", "assigned_to"):
        print(f"  {key}: {t[key]}")


def do_assign(tickets_list):
    ticket_id = prompt("Ticket ID: ")
    staff = prompt("Assign to: ")
    try:
        t = workflow.assign_ticket(tickets_list, ticket_id, staff)
        print(f"{t['id']} assigned to {t['assigned_to']}.")
    except workflow.WorkflowError as e:
        print(f"Error: {e}")


def do_change_status(tickets_list):
    ticket_id = prompt("Ticket ID: ")
    new_status = prompt("New status (open/in_progress/resolved): ")
    try:
        t = workflow.update_status(tickets_list, ticket_id, new_status)
        print(f"{t['id']} is now {t['status']}.")
    except workflow.WorkflowError as e:
        print(f"Error: {e}")


def do_reopen(tickets_list):
    ticket_id = prompt("Ticket ID: ")
    try:
        t = workflow.reopen_ticket(tickets_list, ticket_id)
        print(f"{t['id']} reopened.")
    except workflow.WorkflowError as e:
        print(f"Error: {e}")


def do_queue(tickets_list):
    queue = workflow.get_work_queue(tickets_list)
    print("\n--- Work queue ---")
    if not queue:
        print("Nothing waiting.")
        return
    for t in queue:
        print(f"{t['priority']:>8} | {t['id']} | {t['title']}")


def do_report(tickets_list):
    reports.print_report(tickets_list)


def main():
    try:
        tickets_list = storage.load_tickets(DATA_FILE)
    except storage.StorageError as e:
        print(f"Fatal: {e}")
        sys.exit(1)

    menu = (
        "\n=== CampusFlow ===\n"
        "1. Create ticket\n"
        "2. List tickets\n"
        "3. View ticket\n"
        "4. Assign ticket\n"
        "5. Change status\n"
        "6. Reopen ticket\n"
        "7. Work queue\n"
        "8. Report\n"
        "9. Exit\n"
    )

    actions = {
        "1": lambda: do_create(tickets_list),
        "2": lambda: do_list(tickets_list),
        "3": lambda: do_view(tickets_list),
        "4": lambda: do_assign(tickets_list),
        "5": lambda: do_change_status(tickets_list),
        "6": lambda: do_reopen(tickets_list),
        "7": lambda: do_queue(tickets_list),
        "8": lambda: do_report(tickets_list),
    }

    while True:
        print(menu)
        choice = prompt("Choose: ")

        if choice == "9":
            try:
                storage.save_tickets(tickets_list, DATA_FILE)
                print("Saved. Goodbye.")
            except storage.StorageError as e:
                print(f"Error saving: {e}")
            return

        action = actions.get(choice)
        if action is None:
            print("Invalid option.")
            continue

        action()

        # Save after every mutating action so nothing is lost.
        if choice in {"1", "4", "5", "6"}:
            try:
                storage.save_tickets(tickets_list, DATA_FILE)
            except storage.StorageError as e:
                print(f"Warning: could not save: {e}")


if __name__ == "__main__":
    main()
    