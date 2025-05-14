import frappe
from frappe import _
def execute(filters=None):
    filters = filters or {}

    conditions = {}

    if filters.get("created_by"):
        conditions["created_by"] = filters["created_by"]

    if filters.get("assigned_to"):
        conditions["assigned_to"] = filters["assigned_to"]

    if filters.get("status"):
        conditions["status"] = filters["status"]

    if filters.get("from_date") and filters.get("to_date"):
        conditions["assigned_date"] = ["between", [filters["from_date"], filters["to_date"]]]
    elif filters.get("from_date"):
        conditions["assigned_date"] = [">=", filters["from_date"]]
    elif filters.get("to_date"):
        conditions["assigned_date"] = ["<=", filters["to_date"]]

    data = frappe.get_all(
        "Tasks",
        filters=conditions,
        fields=[
            "task_title",
            "created_by",
            "assigned_to",
            "assigned_date",
            "start_time",
            "end_time",
            "working_hours",
            "status"
        ],
        order_by="assigned_date desc"
    )

    columns = [
        {"label": _("Task Title"), "fieldname": "task_title", "fieldtype": "Data", "width": 200},
        {"label": _("Assigned By"), "fieldname": "created_by", "fieldtype": "Link", "options": "User", "width": 150},
        {"label": _("Assigned To"), "fieldname": "assigned_to", "fieldtype": "Link", "options": "Employee", "width": 150},
        {"label": _("Assigned Date"), "fieldname": "assigned_date", "fieldtype": "Date", "width": 120},
        {"label": _("Start Time"), "fieldname": "start_time", "fieldtype": "Time", "width": 100},
        {"label": _("End Time"), "fieldname": "end_time", "fieldtype": "Time", "width": 100},
        {"label": _("Working Hours"), "fieldname": "workings_hours", "fieldtype": "Float", "width": 120},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Select", "width": 120}
    ]

    return columns, data
