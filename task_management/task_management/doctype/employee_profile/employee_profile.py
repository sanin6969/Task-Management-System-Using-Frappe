# Copyright (c) 2025, Sxnin and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class EmployeeProfile(Document):

    def after_insert(doc):
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
                user.send_welcome_email = 1
                user.insert(ignore_permissions=True)

            roles_to_assign = ["Employee"]
            if doc.is_team_lead:
                roles_to_assign.append("Team Lead")
            if doc.is_hr_manager:
                roles_to_assign.append("HR Manager")

            for role in roles_to_assign:
                if not frappe.db.exists("Has Role", {"parent": user.name, "role": role}):
                    user.append("roles", {"role": role})

            user.save(ignore_permissions=True)

            doc.user = user.name
            frappe.db.set_value("Employee Profile", doc.name, "user", user.name)
            frappe.db.set_value("Employee Profile", doc.name, "password", "")

        if doc.reports_to:
            try:
                team_lead_profile = frappe.get_doc("Employee Profile", {"email": doc.reports_to})
            except frappe.DoesNotExistError:
                frappe.throw(f"Employee Profile with email {doc.reports_to} not found.")
                
            print(team_lead_profile,'#######################')
            
            print(team_lead_profile.user,'********************')
            
            if team_lead_profile.user:
                frappe.get_doc({
                    "doctype": "ToDo",
                    "owner": team_lead_profile.user,
                    "allocated_to": team_lead_profile.user,
                    "description": f"{doc.first_name}  has been assigned to you.",
                    "reference_type": "Employee Profile",
                    "reference_name": doc.name,
                    "assigned_by": frappe.session.user
                }).insert(ignore_permissions=True)
                frappe.get_doc({
                    "doctype": "Notification Log",
                    "for_user": team_lead_profile.user,
                    "type": "Alert",
                    "document_type": "Employee Profile",
                    "document_name": doc.name,
                    "subject": f"{doc.first_name} has been assigned to you.",
                    "email_content": f"{doc.first_name} has been assigned to you by {frappe.session.user}."
                }).insert(ignore_permissions=True)

def has_permission(self, ptype):
        user = frappe.session.user
        roles = frappe.get_roles(user)

        if "HR Manager" in roles:
            return True

        if self.user == user:
            return True

        if "Team Lead" in roles:
            lead_profile_name = frappe.db.get_value("Employee Profile", {"user": user}, "name")
            if lead_profile_name and self.reports_to == lead_profile_name:
                return True

        return False
