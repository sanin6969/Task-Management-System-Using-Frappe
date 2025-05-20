import frappe
from frappe.utils import getdate, add_days, nowdate

def send_task_due_reminders():
    # frappe.logger().info(">>> send_task_due_reminders triggered")
    # print(">>> send_task_due_reminders triggered")
    target_date = getdate(add_days(nowdate(), 2))

    tasks = frappe.get_all("Project Task",  
        filters={"due_date": target_date},
        fields=["name", "due_date", "assigned_to", "task_name","status"]
    )

    for task in tasks:
        if not task.assigned_to:
            continue
        if task.status != "Completed":
            user_email = frappe.db.get_value("Employee Profile", task.assigned_to, "email")
            if not user_email:
                continue

            subject = f"Upcoming Task Due: {task.task_name}"
            message = f"""
            Hello,<br><br>
            This is a reminder that your task <b>{task.task_name}</b> is due on <b>{task.due_date}</b>.<br><br>
            Regards,<br>Task Management System
            """

            frappe.enqueue(send_reminder_notification,
                queue='default',
                timeout=300,
                task_name=task.task_name,
                user_email=user_email,
                subject=subject,
                message=message
            )
            user = frappe.get_value("Employee Profile", {"name": task.assigned_to}, "user")
            frappe.get_doc({
                "doctype": "Notification Log",
                "for_user": user,
                "type": "Alert",
                "document_type": "Project Task",
                "document_name": task.name,
                "subject": f"Task Due Soon: {task.task_name}",
                "email_content": f"Task <b>{task.task_name}</b> is due on <b>{task.due_date}</b>."
            }).insert(ignore_permissions=True)

        
def update_overdue_tasks():
    frappe.logger().info(">>> update_overdue_tasks triggered")
    print(">>> update_overdue_tasks triggered")
    today = getdate(nowdate())
    print(today,'today')
    # tomorrow = add_days(today, 1)
    tasks = frappe.get_all("Project Task",  
        filters={
            "due_date": ["in", [today]],
            "status": ["in", ["Not Started", "Started"]]
        },
        fields=["name"]
    )
    print(tasks,'ttttttttttttttttttttttt')
    for task in tasks:
        doc = frappe.get_doc("Project Task", task.name)
        print(doc.task_name,'doc name')
        doc.status = "Overdue"
        doc.save(ignore_permissions=True)
        print("statuss",doc.status)
        
        
        
        
def send_reminder_notification(task_name, user_email, subject, message):
    frappe.sendmail(
        recipients=[user_email],
        subject=subject,
        message=message
    )
    

