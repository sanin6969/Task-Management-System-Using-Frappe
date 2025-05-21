import frappe
from frappe import _
from datetime import datetime
from frappe.utils import get_datetime,getdate
@frappe.whitelist()
def get_team_members(doctype, txt, searchfield, start, page_len, filters):
    user = frappe.session.user
    employees = frappe.get_all("Employee Profile",
        filters={"reports_to": user},
        fields=["user","email"],
        limit_page_length=page_len,
        start=start
    )
    return [[emp.email] for emp in employees if emp.user]

# def get_permission_query_conditions(user):
#     if not user: return ""
#     if "HR Manager" in frappe.get_roles(user):
#         return ""
#     return f"""(`tabProject`.`team_lead` = '{user}')"""

def user_email_to_employee_email(doc, method, old_email=None, new_email=None, merge=False):
    name,email = frappe.db.get_value("Employee Profile",{"email":old_email},["name","email"])        
    if email != new_email:
        frappe.db.set_value("Employee Profile", name, "email", new_email)


@frappe.whitelist()
def get_remaining_leaves(user, leave_type):
    employee = frappe.get_doc("Employee Profile", {"user": user})
    if leave_type == "Sick Leave":
        return {"remaining": employee.sick_leave_remaining}
    elif leave_type == "Casual Leave":
        return {"remaining": employee.casual_leave_remaining}
    return {"remaining": 0}



@frappe.whitelist()
def add_task_comment(docname, comment_text):
    doc = frappe.get_doc("Tasks", docname)
    doc.add_comment("Comment", comment_text)
    return "Comment added successfully"

@frappe.whitelist()
def mark_project_completed_employee(project_name):
    user = frappe.session.user
    doc = frappe.get_doc("Project", project_name)
    updated_tasks = []
    blocked_tasks = []
    already_completed = []

    for task_row in doc.get("task", []):
        # print(task_row.task_name,'c ttttttttttttttttttttt nnnaaaaammmmmeeee')
        if task_row.assigned_to == user:
            if task_row.status == "Started" or task_row.status == "Overdue":
                emp_tasks =  frappe.get_doc("Tasks",task_row.task_name)
                # print(emp_tasks,'empppppppppppppppppppp')
                task_row.status = "Completed"
                emp_tasks.status="Completed"
                emp_tasks.end_time = datetime.now()
                emp_tasks.workings_hours = round(
                        (get_datetime(emp_tasks.end_time) - get_datetime(emp_tasks.start_time)).total_seconds() / 3600, 2
                    )
                task_row.working_hours = emp_tasks.workings_hours
                task_row.start_date = getdate(emp_tasks.start_time)
                task_row.end_date = getdate(emp_tasks.end_time)
                task_row.save()
                emp_tasks.save()
                updated_tasks.append(task_row.task_name)
            elif task_row.status == "Not Started":
                blocked_tasks.append(task_row.task_name)
            elif task_row.status == "Completed":
                already_completed.append(task_row.task_name)

    return {
        "updated_tasks": updated_tasks,
        "blocked_tasks": blocked_tasks,
        "already_completed": already_completed,
    }
            
        



@frappe.whitelist()
def mark_project_completed(project_name):
    doc = frappe.get_doc("Project", project_name)
    incomplete_tasks = []
    for task in doc.get("task", []):
        if task.status != "Completed":
            incomplete_tasks.append({
                "task_name": task.task_name,
                "assigned_to": task.assigned_to
            })

    if not incomplete_tasks:
        doc.status = "Completed"
        doc.save()
        return {"status": "completed"}
    else:
        return {
            "status": "incomplete",
            "incomplete_tasks": incomplete_tasks
        }

@frappe.whitelist()
def send_task_reminders(project_name):
    doc = frappe.get_doc("Project", project_name)

    for task in doc.get("task", []):
        if task.status != "Completed" and task.assigned_to:
            title = f"Reminder to complete task: {task.task_name}"
            message = f"You are assigned to task <b></b> in project <b>{project_name}</b>. Please complete it as soon as possible."
                        
            frappe.get_doc({
            "doctype": "Notification Log",
            "for_user": task.assigned_to,
            "type": "Alert",
            "document_type": "Project Task",
            "document_name": task.name,
            "subject": title,
            "email_content": message
        }).insert(ignore_permissions=True)
            

