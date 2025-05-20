frappe.query_reports["Task Reports"] = {
    "filters": [
        {
            "fieldname": "created_by",
            "label": __("Created By"),
            "fieldtype": "Link",
            "options": "User"
        },
        {
            "fieldname": "assigned_to",
            "label": __("Assigned To"),
            "fieldtype": "Link",
            "options": "Employee Profile"
        },
        {
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": "\nDraft\nAssigned\nIn Progress\nCompleted"
        },
        // {
        //     "fieldname": "from_date",
        //     "label": __("From Date"),
        //     "fieldtype": "Date"
        // },
        // {
        //     "fieldname": "to_date",
        //     "label": __("To Date"),
        //     "fieldtype": "Date"
        // }
    ]
};
