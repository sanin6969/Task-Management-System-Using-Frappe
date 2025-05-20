frappe.query_reports["Project Report"] = {
    "filters": [
        {
            "fieldname": "status",
            "label": "Project Status",
            "fieldtype": "Select",
            "options": ["", "In Progress", "Completed"],
            "default": "In Progress"
        }
    ]
};
