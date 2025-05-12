frappe.query_reports["Task Report"] = {
    filters: [
        {
            fieldname: "created_by",
            label: "Created By",
            fieldtype: "Link",
            options: "User"
        },
        {
            fieldname: "assigned_to",
            label: "Assigned To",
            fieldtype: "Link",
            options: "Employee"
        },
        {
            fieldname: "status",
            label: "Status",
            fieldtype: "Select",
            options: ["", "Draft", "Assigned", "In Progress", "Completed"]
        },
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date"
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date"
        }
    ]
};
