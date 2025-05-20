import frappe

def execute(filters=None):
    columns = [
        {"label": "Project Name", "fieldname": "project_name", "fieldtype": "Data", "width": 200},
        {"label": "Team Lead", "fieldname": "team_lead", "fieldtype": "Data", "width": 150},
        {"label": "Start Date", "fieldname": "start_date", "fieldtype": "Date", "width": 120},
        {"label": "End Date", "fieldname": "end_date", "fieldtype": "Date", "width": 120},
        {"label": "% Tasks Completed", "fieldname": "percent_complete", "fieldtype": "Percent", "width": 150},
        {"label": "Overall Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
    ]

    data = []
    filter_status = filters.get("status") if filters else None

    project_filters = {}
    if filter_status:
        project_filters["status"] = filter_status

    projects = frappe.get_all("Project",
        filters=project_filters,
        fields=["name", "project_name", "start_date", "end_date", "team_lead", "status"]
    )

    for proj in projects:
        task_children = frappe.get_all("Project Task", 
            filters={"parent": proj.name, "parenttype": "Project"},
            fields=["status"]
        )

        total_tasks = len(task_children)
        completed_tasks = sum(1 for t in task_children if t.status == "Completed")
        percent = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0

        data.append({
            "project_name": proj.project_name,
            "team_lead": proj.team_lead,
            "start_date": proj.start_date,
            "end_date": proj.end_date,
            "percent_complete": round(percent, 2),
            "status": proj.status
        })

    return columns, data
