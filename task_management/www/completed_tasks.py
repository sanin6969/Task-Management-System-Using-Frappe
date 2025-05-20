# # my_app/www/my-tasks/index.py

# import frappe

# def get_context(context):
#     current_user = frappe.session.user

#     context.tasks = frappe.get_all(
#         "Project Task",
#         filters={
#             "assigned_to": current_user,
#             "status": ["!=", "Completed"],
#         },
#         fields=[
#             "task_name",
#             "status",
#             "due_date",
#             "linked_tasks",
#             "parent as project_name"
#         ],
#         order_by="due_date asc"
#     )

#     return context




import frappe
from frappe.utils import nowdate

import frappe

import frappe

def get_context(context):
    user = frappe.get_value("Employee Profile", {"email": frappe.session.user}, "name")

    # Get filters from query params
    selected_project = frappe.form_dict.get("project_name")
    selected_status = frappe.form_dict.get("status")

    # Build dynamic filters
    filters = {
        "assigned_to": user
    }
    if selected_project:
        filters["parent"] = selected_project
    if selected_status:
        filters["status"] = selected_status

    # Fetch tasks with filters
    project_tasks = frappe.get_all(
        "Project Task",
        filters=filters,
        fields=[
            "task_name",
            "status",
            "due_date",
            "start_date",
            "end_date",
            "linked_task",
            "parent as project_name"
        ],
    )

    # Attach linked task data
    for task in project_tasks:
        if task.linked_task:
            try:
                linked_doc = frappe.get_doc("Tasks", task.linked_task)
                task.linked_task_data = {
                    "task_title": linked_doc.task_title,
                    "start_time": linked_doc.start_time,
                    "end_time": linked_doc.end_time,
                    "working_hours": linked_doc.working_hours,
                    "project_name": linked_doc.project_name,
                }
            except frappe.DoesNotExistError:
                task.linked_task_data = None
        else:
            task.linked_task_data = None

    all_tasks = frappe.get_all(
        "Project Task",
        filters={"assigned_to": user},
        fields=["status", "parent"]
    )

    project_names = sorted(set(task.parent for task in all_tasks if task.parent))
    statuses = sorted(set(task.status for task in all_tasks if task.status))

    context.tasks = project_tasks
    context.project_names = project_names
    context.statuses = statuses
    context.selected_project = selected_project
    context.selected_status = selected_status

    return context
