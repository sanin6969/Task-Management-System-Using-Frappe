import frappe
from frappe.model.document import Document
from frappe.desk.form.assign_to import add
from frappe.model.rename_doc import rename_doc
class EmployeeProfile(Document):
    def on_update(self):
        if self.user:
            try:
                user = frappe.get_doc("User", self.user)
            except Exception as e:
                print("Error updating user email:", e)
                

            if self.email and self.email != user.email:
                if frappe.db.exists("User", self.email):
                    frappe.throw(f"Email {self.email} is already assigned to another user")
                
                frappe.db.savepoint("employee_update")
                try:
                    rename_doc("User", user.name, self.email, ignore_permissions=True)
                    frappe.db.set_value("Employee Profile", self.name, "user", self.email)
                except Exception as e:
                    frappe.db.rollback_savepoint("employee_update")
                    frappe.throw(str(e))
                
    def after_insert(doc):
        if doc.reports_to:
            if doc.roles:
                for i in doc.roles:
                    if i.roles in ["HR Manager", "Team Lead"]:
                        frappe.throw("An HR Manager or Team Lead cannot be reported to someone.")
            try:
                team_lead_profile = frappe.get_doc("Employee Profile", {"email": doc.reports_to})
            except frappe.DoesNotExistError:
                frappe.throw(f"Employee Profile {doc.reports_to} not found.")
                
            if team_lead_profile.user:
                add({
                    "assign_to": [team_lead_profile.user],
                    "doctype": "Employee Profile",
                    "name": doc.name,
                    "description": f"{doc.first_name} has been assigned to you.",
                    "assigned_by": frappe.session.user
                })

                frappe.get_doc({
                    "doctype": "Notification Log",
                    "for_user": team_lead_profile.user,
                    "type": "Alert",
                    "document_type": "Employee Profile",
                    "document_name": doc.name,
                    "subject": f"{doc.first_name} has been assigned to you.",
                }).insert(ignore_permissions=True)
                
        if not doc.user:
            if frappe.db.exists("User", {"email": doc.email}):
                user = frappe.get_doc("User", {"email": doc.email})
            else:
                user = frappe.new_doc("User")
                user.email = doc.email
                user.first_name = doc.first_name
                user.last_name = doc.last_name
                user.username = doc.email.split('@')[0]
                user.enabled = 1
                user.new_password = "plmnkoijb"
                user.send_welcome_email = 0
                user.insert(ignore_permissions=True)

            roles_to_assign = {"Employee"}
            if doc.roles:
                for r in doc.roles:
                    roles_to_assign.add(r.roles)

            for role in roles_to_assign:
                if not frappe.db.exists("Has Role", {"parent": user.name, "role": role}):
                    user.append("roles", {"role": role})
            user.save(ignore_permissions=True)
            frappe.sendmail(
                recipients=[doc.email],
                subject= f"Welcome to Task Management , {doc.first_name}",
                template="UserWelcomeEmail",
                args={
                    "doc": doc,  
                    "password": 'plmnkoijb' 
                },
                reference_doctype="Employee Profile",
                reference_name=doc.name,
            )
            doc.user = user.name
            frappe.db.set_value("Employee Profile", doc.name, "user", user.name)
            frappe.db.set_value("Employee Profile", doc.name, "password", "")
        





