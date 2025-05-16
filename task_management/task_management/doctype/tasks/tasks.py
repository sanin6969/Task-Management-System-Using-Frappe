from frappe.model.document import Document
import frappe
from frappe import _
from datetime import datetime
from frappe.utils import get_datetime


class Tasks(Document):
    
    def before_insert(self):
        self.created_by = frappe.session.user
    def _get_user_roles(self):
        current_user = frappe.session.user
        # print(current_user,'cccccccurrrrrrrreeeentt uuuuussssssseeeeeeerrrrrr')
        is_employee = frappe.db.exists("Employee Profile", {"user": current_user})
        # print(is_employee,'iiiiiiisssssssssss eeemmmmmmppppplooyeeee')
        is_team_lead = "Team Lead" in frappe.get_roles()
        return current_user, is_employee, is_team_lead
    
    def validate(self):
        current_user, is_employee, is_team_lead = self._get_user_roles()
        
        if is_team_lead:
            if self.status == "Assigned" and not self.assigned_to:
                frappe.throw(_("Assigned To is required when status is 'Assigned'"))
            if self.status == "Draft" and self.assigned_to:
                frappe.throw(_("Assigned To must be empty when status is 'Draft'"))
            
            if self.status == "Assigned" and not self.assigned_date:
                self.assigned_date = frappe.utils.nowdate()
                
        elif is_employee:
            if self.status not in ["In Progress", "Completed"]:
                frappe.throw(_("Employees can only set status to In Progress or Completed"))
            
            if self.status == "In Progress" and not self.start_time:
                self.start_time = datetime.now()
            elif self.status == "Completed" and not self.end_time:
                self.end_time = datetime.now()
                if self.start_time:
                    self.workings_hours = round(
                        (get_datetime(self.end_time) - get_datetime(self.start_time)).total_seconds() / 3600, 2
                    )

    def on_update(self):
        current_user, is_employee, is_team_lead = self._get_user_roles()
        if is_team_lead and self.status == "Assigned":
            self.send_assignment_notification()
        elif is_employee and self.status == "Completed":
            self.send_completed_notification()
            
        project_tasks = frappe.get_all(
                "Task",  
                filters={"task_name": self.name}, 
                fields=["name", "parent", "parenttype"]
            )
        if self.status == "In Progress":
            for pt in project_tasks:
                frappe.db.set_value("Task", pt.name, "status", "Started")
        if self.status == "Completed":
            for pt in project_tasks:
                frappe.db.set_value("Task", pt.name, "status", "Completed")
            
                
        # project_name = self.project_name  
        # print(project_name,'nnnnnnnnnnnnnnnnnnnnn')
        # if project_name:
        #     project_doc = frappe.get_doc("Project", project_name)
        #     if project_doc.status != "In Progress":
        #         project_doc.status = "In Progress"
        #         project_doc.save()

    # def after_insert(self):
        # print('wwwwwwwwwwwwwwwwwwwwwww')
        
    def send_completed_notification(self):
        frappe.get_doc({
            "doctype": "Notification Log",
            "for_user": self.created_by,
            "type": "Alert",
            "document_type": "Tasks",
            "document_name": self.name,
            "subject": f"Task completed by {self.assigned_to}",
            "email_content": f"The Task {self.name} Assigned to {self.assigned_to} is  Complted</b>."
        }).insert(ignore_permissions=True)
    
    def send_assignment_notification(self):
        if not self.assigned_to:
            return  
        task_name = self.name 
        creator = frappe.get_value("User", self.created_by, "full_name") or self.created_by
        assignee = frappe.get_value("Employee Profile", {"name": self.assigned_to}, "user")

        frappe.get_doc({
            "doctype": "ToDo",
            "owner": assignee,
            "allocated_to": assignee,
            "description": f"{creator} has assigned you the task: {task_name}.",
            "assigned_by": self.created_by,
            "reference_type": "Tasks",
            "reference_name": self.name
        }).insert(ignore_permissions=True)

        frappe.get_doc({
            "doctype": "Notification Log",
            "for_user": assignee,
            "type": "Alert",
            "document_type": "Tasks",
            "document_name": self.name,
            "subject": f"New Task Assigned: {task_name}",
            "email_content": f"{creator} has assigned you a new task: <b>{task_name}</b>."
        }).insert(ignore_permissions=True)






def get_permission_query_conditions(user):
    if "HR Manager" in frappe.get_roles(user):
        return ""
    employee_name = frappe.db.get_value("Employee Profile", {"user": user}, "name")
    # print(employee_name,'emp naaaaaaaaaaaammmmmmmmeeeeeeee')
    return f"""(tabTasks.created_by = '{user}' OR tabTasks.assigned_to = '{employee_name}')"""






























# def has_permission(doc, ptype):
#     user = frappe.session.user  
#     print(user,'uuuuuuuuussssssssserrrrrrrr')
#     if "HR Manager" in frappe.get_roles(user):
#         return True
#     if doc.owner == user:
#             return True

#     employee_name = frappe.db.get_value("Employee Profile", {"user": user}, "name")
#     return doc.created_by == user or doc.assigned_to == employee_name