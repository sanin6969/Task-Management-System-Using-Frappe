import frappe

def get_context(context):
    context.tasks = frappe.get_all(
        "Tasks",
        # filters={"status": "Completed"},
        fields=[ "task_title", "status", "created_by","assigned_to"],
    )
    return context
