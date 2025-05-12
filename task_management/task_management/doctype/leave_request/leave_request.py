# Copyright (c) 2025, Sxnin and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LeaveRequest(Document):
	pass

def has_permission(doc, user):
    print('workingggggggggg')
    roles = frappe.get_roles(user)
    print(roles, 'rrrrooooooooooolleeeeeees') 

    if "HR Manager" in roles:
        print(doc.workflow_state,'wwwwwwwwwooooooooorrrk sssssstttttttaaattttte')
        return doc.workflow_state == "Pending HR Approval"


    if "Team Lead" in roles:
        team_lead_profile = frappe.get_value("Employee Profile", {"user_id": user}, "name")
        if not team_lead_profile:
            return False

        employee_reports_to = frappe.get_value("Employee Profile", doc.employee, "reports_to")
        return employee_reports_to == team_lead_profile

    if "Employee" in roles:
        return doc.owner == user

    return False






    

    
