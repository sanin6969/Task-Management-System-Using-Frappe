from frappe.model.document import Document
import frappe
from frappe import _
from datetime import datetime
from frappe.utils import get_datetime,getdate


class Tasks(Document):
    
    def before_insert(self):
        self.created_by = frappe.session.user
    def _get_user_roles(self):
        is_employee = frappe.db.exists("Employee Profile", {"user": frappe.session.user})
        is_team_lead = "Team Lead" in frappe.get_roles()
        print(is_team_lead,'taem llllllllllllllllll')
        return is_employee, is_team_lead
    
    def validate(self):
        print('workingggggggggggggggggggggggggggggggggggggg')
        is_employee, is_team_lead = self._get_user_roles()
        
        if is_team_lead:
            print('[workingssssssssssssssssssssssssssssssssssssssss')
            if self.status == "Assigned" and not self.assigned_date:
                print('assssssssssssssssingned')
                self.assigned_date = frappe.utils.nowdate()
            if self.status == "Draft" and self.assigned_to:
                frappe.throw(_("Assigned To must be empty when status is 'Draft'"))
                
            if self.status == "Assigned" and not self.assigned_to:
                frappe.throw(_("You should Assign a user if the status is 'Assigned'"))
            
            

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
        if self.status == "In Progress":
            if self.project_name:
                project_doc = frappe.get_doc("Project", self.project_name)
                if project_doc.status != "In Progress":
                    project_doc.status = "In Progress"
                    project_doc.save()
             
    def on_update(self):
        is_employee, is_team_lead = self._get_user_roles()
        if is_team_lead and self.status == "Assigned":
            self.send_assignment_notification()
        elif is_employee and self.status == "Completed":
            self.send_completed_notification()
            
        project_tasks = frappe.get_all(
            "Project Task",  
            filters={"task_name": self.name}, 
            fields=["name"]
        )

        if not project_tasks:
            return

        update_fields = {}
        if self.status == "In Progress":
            update_fields["status"] = "Started"
        elif self.status == "Completed":
            update_fields["status"] = "Completed"

        if self.assigned_to:
            update_fields["assigned_to"] = self.assigned_to
        if self.workings_hours:
            update_fields["working_hours"] = self.workings_hours
        if self.start_time:
            update_fields["start_date"] = getdate(self.start_time)
        if self.end_time:
            update_fields["end_date"] = getdate(self.end_time)

        if update_fields:
            frappe.db.set_value(
                "Project Task",
                {"name": ("in", [pt.name for pt in project_tasks])},
                update_fields,
                update_modified=False
            )
            

        
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