# CampusFlow

A command-line helpdesk ticket manager for Learn2Earn campus staff.

## The problem

Campus staff report technical issues informally — over WhatsApp, in person, or
in passing — and requests get lost. CampusFlow replaces that with a structured
record: every request becomes a ticket with a validated category, a calculated
priority, an assignee, and a tracked lifecycle. Tickets survive restarts by
being persisted to a JSON file.

## Team

| Fellow | Role | Contributions |
|---|---|---|
| Joe-Adobunu | Engineer A | `campusflow/tickets.py`, `campusflow/storage.py`, `tests/test_tickets.py`, `tests/test_storage.py`, `README.md`, `docs/` |
| Yimasolomon | Engineer B | `campusflow/workflow.py`, `campusflow/reports.py`, `main.py`, `tests/test_workflow.py` |

Both fellows reviewed each other's pull requests before merge. See the
[PR history](https://github.com/Joe-Adobunu/CampusFlow/pulls?q=is%3Apr) for
evidence.

## Requirements

- **Python 3.10 or later** (uses `os.replace`, union types in type hints not
  required, but modern Python is recommended)
- No third-party dependencies. Standard library only: `json`, `os`,
  `unittest`, `tempfile`.

## Setup

```bash
git clone https://github.com/Joe-Adobunu/CampusFlow.git
cd CampusFlow
# Optional: create a virtual environment
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
