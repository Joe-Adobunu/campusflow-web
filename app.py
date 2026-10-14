"""
CampusFlow web application.

Thin HTTP layer over the existing campusflow/* modules.
Run locally with:  flask --app app run --debug
"""

import os
from flask import Flask, jsonify, request, render_template, redirect, url_for

from campusflow import reports, storage, tickets, workflow

app = Flask(__name__)

DATA_FILE = os.path.join("data", "tickets.json")


def _load():
    """Load tickets, returning [] if the file is missing or corrupt."""
    try:
        return storage.load_tickets(DATA_FILE)
    except storage.StorageError:
        return []


def _save(ticket_list):
    storage.save_tickets(ticket_list, DATA_FILE)


# ---------------------------------------------------------------------------
# HTML pages
# ---------------------------------------------------------------------------

@app.get("/")
def index():
    ticket_list = _load()
    queue = workflow.get_work_queue(ticket_list)
    report = reports.generate_report(ticket_list)
    return render_template("index.html",
                           tickets=ticket_list,
                           queue=queue,
                           report=report)


@app.post("/create")
def create():
    title = request.form.get("title", "").strip()
    category = request.form.get("category", "").strip()
    urgency = request.form.get("urgency", "").strip()
    users_raw = request.form.get("affected_users", "").strip()

    try:
        affected_users = int(users_raw)
        ticket_list = _load()
        tickets.create_ticket(ticket_list, title, category, urgency, affected_users)
        _save(ticket_list)
    except (ValueError, tickets.ValidationError) as e:
        return render_template("error.html", message=str(e)), 400

    return redirect(url_for("index"))


@app.post("/assign/<ticket_id>")
def assign(ticket_id):
    staff = request.form.get("staff_name", "").strip()
    try:
        ticket_list = _load()
        workflow.assign_ticket(ticket_list, ticket_id, staff)
        _save(ticket_list)
    except workflow.WorkflowError as e:
        return render_template("error.html", message=str(e)), 400
    return redirect(url_for("index"))


@app.post("/status/<ticket_id>")
def status(ticket_id):
    new_status = request.form.get("new_status", "").strip()
    try:
        ticket_list = _load()
        workflow.update_status(ticket_list, ticket_id, new_status)
        _save(ticket_list)
    except workflow.WorkflowError as e:
        return render_template("error.html", message=str(e)), 400
    return redirect(url_for("index"))


# ---------------------------------------------------------------------------
# JSON API (useful for testing / future frontend)
# ---------------------------------------------------------------------------

@app.get("/api/tickets")
def api_tickets():
    return jsonify(_load())


@app.get("/api/queue")
def api_queue():
    return jsonify(workflow.get_work_queue(_load()))


@app.get("/api/report")
def api_report():
    return jsonify(reports.generate_report(_load()))


if __name__ == "__main__":
    app.run(debug=True)
    