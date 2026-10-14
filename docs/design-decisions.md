# Design Decisions — CampusFlow

Agreements made **before** writing code (guide §2.2). Each decision records
the choice, the alternative considered, and the reasoning.

---

## 1. Team and ownership

| Fellow | Owns | Tests |
|---|---|---|
| Joe-Adobunu | `campusflow/tickets.py`, `campusflow/storage.py` | `tests/test_tickets.py`, `tests/test_storage.py` |
| Yimasolomon | `campusflow/workflow.py`, `campusflow/reports.py`, `main.py` | `tests/test_workflow.py` |
| Both | `README.md`, `docs/`, cross-review of each other's PRs | — |

Every fellow writes application code **and** matching tests. Neither of us
only writes documentation.

---

## 2. Data structures

**Decision:** a ticket is a plain `dict`. The ticket collection is a
`list[dict]`.

**Example ticket:**

```python
{
    "id": "T001",
    "title": "Campus Wi-Fi is down",
    "category": "Network",
    "urgency": "high",
    "affected_users": 15,
    "priority": "critical",
    "status": "open",
    "assigned_to": None,
}
