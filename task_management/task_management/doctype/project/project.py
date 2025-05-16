# Copyright (c) 2025, Sxnin and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate
import datetime
class Project(Document):
    def validate(self):
        today = datetime.date.today()
        
        print(today)
        
        start_date = getdate(self.start_date)
        end_date = getdate(self.end_date)
        if start_date < today:
            frappe.throw("Start date cannot be in the past.")

        if end_date < today:
            frappe.throw("End date cannot be in the past.")

        if end_date < start_date:
            frappe.throw("End date cannot be before start date.")
        
				

    def on_update(self):
        for row in self.task:
            if row.task_name:
                task_doc = frappe.get_doc("Tasks", row.task_name)
                row.assigned_to = task_doc.assigned_to
                row.due_date = self.end_date
                row.save()
               
        user_roles = frappe.get_roles(frappe.session.user)
        if "HR Manager" in user_roles and self.team_lead:
            self.send_assigned_notification()

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
