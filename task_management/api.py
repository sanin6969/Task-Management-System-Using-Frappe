import frappe
from frappe import _

@frappe.whitelist()
def get_team_members(doctype, txt, searchfield, start, page_len, filters):
    user = frappe.session.user
    lead_profile = frappe.get_doc("Employee Profile", {"user": user})    
    employees = frappe.get_all("Employee Profile",
        filters={"reports_to": lead_profile.email},
        fields=["name", "user"],
        limit_page_length=page_len,
        start=start
    )
    return [[emp.name] for emp in employees if emp.user]

def get_permission_query_conditions(user):
    if not user: return ""
    if "HR Manager" in frappe.get_roles(user):
        return ""
    return f"""(`tabProject`.`team_lead` = '{user}')"""

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