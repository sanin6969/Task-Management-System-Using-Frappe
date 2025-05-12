from frappe.model.document import Document
import frappe
from frappe import _
from datetime import datetime
from frappe.utils import get_datetime


class Tasks(Document):
    
    def before_insert(self):
        self.created_by = frappe.session.user
        
    def on_update(self):
        current_user = frappe.session.user

        is_employee = frappe.db.exists("Employee Profile", {"user": current_user})
        is_team_lead = "Team Lead" in frappe.get_roles()

        if is_team_lead:
            allowed_statuses = ["Draft", "Assigned"]
            if self.status not in allowed_statuses:
                frappe.throw(_(f"Team Lead can only update the task status to {allowed_statuses}. You cannot set it to '{self.status}'."))


            if self.assigned_to and not self.assigned_date:
                self.assigned_date = frappe.utils.nowdate()
                
            if self.status == "Assigned":
                if not self.assigned_to :
                    frappe.throw(_("When status is 'Assigned', 'Assigned To' field  is required."))

                self.send_assignment_notification()

            if self.status == "Draft":
                if self.assigned_to :
                    frappe.throw(_("When status is 'Draft', 'Assigned To'  must be empty."))

        elif is_employee:
            allowed_statuses = ["In Progress", "Completed"]
            if self.status not in allowed_statuses:
                frappe.throw(_(f"Employee can only update the task status to {allowed_statuses}. You cannot set it to '{self.status}'."))

            if self.status == "In Progress":
                self.start_time = datetime.now()
                print(self.start_time,'ssssssstaaaaaaartttt timeee')
            if self.status == "Completed":
                self.end_time = datetime.now()

                self.start_time = get_datetime(self.start_time)
                self.end_time = get_datetime(self.end_time)
                print(self.start_time,'ssssssstaaaaaaartttt timeee')
                print(self.end_time,'ssssssstaaaaaaartttt timeee')

                time_diff = self.end_time - self.start_time
                print(time_diff,'timeee ddddddddddiiiiiiiiifffffffff')
                self.working_hours = round(time_diff.total_seconds() / 3600, 2)
                print(self.working_hours,'wwwwwwwwwwwwwroooooookkkkkking hooouuuuurrrssssss')
                self.send_completed_notification()

    def send_completed_notification(self):
        print(self.assigned_to,'assigned tpooooooo')
        print(self.created_by,'createdddddd byyyyyyy')
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

        task_name = self.name or "a task"
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
    if not user:
        return ""

    if "HR Manager" in frappe.get_roles(user):
        return ""

    employee_name = frappe.db.get_value("Employee Profile", {"user": user}, "name")
    return f"""(tabTasks.created_by = '{user}' OR tabTasks.assigned_to = '{employee_name}')"""


def has_permission(doc, ptype):
    user = frappe.session.user  
    if "HR Manager" in frappe.get_roles(user):
        return True
    if doc.owner == user:
            return True

    employee_name = frappe.db.get_value("Employee Profile", {"user": user}, "name")
    return doc.created_by == user or doc.assigned_to == employee_name





