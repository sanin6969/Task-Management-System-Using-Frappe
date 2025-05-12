import frappe

def execute(filters=None):
    filters = filters or {}

    conditions = {}

    if filters.get("created_by"):
        conditions["created_by"] = filters.get("created_by")

    if filters.get("assigned_to"):
        conditions["assigned_to"] = filters.get("assigned_to")

    if filters.get("status"):
        conditions["status"] = filters.get("status")

    if filters.get("from_date") and filters.get("to_date"):
        conditions["assigned_date"] = ["between", [filters.get("from_date"), filters.get("to_date")]]
    elif filters.get("from_date"):
        conditions["assigned_date"] = [">=", filters.get("from_date")]
    elif filters.get("to_date"):
        conditions["assigned_date"] = ["<=", filters.get("to_date")]

    data = frappe.get_all("Tasks",
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
        {"label": "Task Title", "fieldname": "task_title", "fieldtype": "Data", "width": 200},
        {"label": "Assigned By", "fieldname": "created_by", "fieldtype": "Link", "options": "User", "width": 150},
        {"label": "Assigned To", "fieldname": "assigned_to", "fieldtype": "Link", "options": "Employee Profile", "width": 150},
        {"label": "Start Time", "fieldname": "start_time", "fieldtype": "Time", "width": 100},
        {"label": "End Time", "fieldname": "end_time", "fieldtype": "Time", "width": 100},
        {"label": "Status", "fieldname": "status", "fieldtype": "Select", "width": 120}
    ]

    return columns, data
