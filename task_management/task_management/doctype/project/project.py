import frappe
from frappe.model.document import Document
from frappe.utils import getdate
import datetime
from frappe import _
from frappe.share import add as add_share
class Project(Document):
    def validate(self):
        today = datetime.date.today()
        start_date = getdate(self.start_date)
        end_date = getdate(self.end_date)

        if not self.name:  
            if start_date < today:
                frappe.throw("Start date cannot be in the past.")
            if end_date < today:
                frappe.throw("End date cannot be in the past.")

        if end_date < start_date:
            frappe.throw("End date cannot be before start date.")

        for task in self.task:
            due_date = getdate(task.due_date)
            if due_date > end_date:
                frappe.throw(f"Task '{task.task_name}' has a due date beyond the project end date.")
            if due_date < start_date:
                frappe.throw(f"Task '{task.task_name}' has a due date before the project start date.")
				
               
    def on_update(self):
        self.create_independent_tasks()
        self.share_project()
    def share_project(self):
        current_user = frappe.session.user
        user_roles = frappe.get_roles(current_user)

        try:
            if "HR Manager" in user_roles and self.team_lead:
                add_share("Project", self.name, user=self.team_lead, read=1, write=1, submit=0, share=1, everyone=0, notify=1)

            elif "Team Lead" in user_roles:
                add_share("Project", self.name, user=current_user, read=1, write=1, submit=0, share=1, everyone=0, notify=0)
                
        except Exception as e:
            frappe.log_error(f"Error sharing project: {frappe.get_traceback()}")
                
    def create_independent_tasks(self):
        for task_row in self.task:
            if not task_row.linked_task:
                existing_task = frappe.db.exists("Tasks", {
                    "task_title": task_row.task_name,
                    "project_name": self.name
                })
                if existing_task:
                    task_row.linked_task = existing_task
                else:
                    task_doc = frappe.new_doc("Tasks")
                    task_doc.task_title = task_row.task_name
                    task_doc.project_name = self.name
                    task_doc.insert()
                    task_row.linked_task = task_doc.name

    def send_assigned_notification(self):
        frappe.get_doc({
            "doctype": "Notification Log",
            "for_user": self.team_lead,
            "type": "Alert",
            "document_type": "Project",
            "document_name": self.name,
            "subject": f"New Project Assigned: {self.name}",
            "email_content": f"<b>HR MANAGER</b> has assigned you a new project: <b>{self.name}</b>."
        }).insert(ignore_permissions=True)





# def has_permission(doc, user):
#     print(user,'aaaaaaaaaaaaaaaaaaaaaaaaa')
#     if "HR Manager" in frappe.get_roles(user):
#         return True
#     if doc.team_lead == user:
#         return True
#     if frappe.db.exists("Project Task", {"parent": doc.name, "parenttype": "Project", "assigned_to": user}):
#         return True
#     return False


