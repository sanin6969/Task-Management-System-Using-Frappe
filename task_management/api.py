import frappe
from frappe import _

@frappe.whitelist()
def get_team_members(doctype, txt, searchfield, start, page_len, filters):
    user = frappe.session.user

    if "Team Lead" not in frappe.get_roles(user):
        frappe.throw(_("You are not authorized to assign tasks"))

    lead_profile = frappe.get_doc("Employee Profile", {"user": user})
    
    print(lead_profile.email,'////////////')
    
    employees = frappe.get_all("Employee Profile",
        filters={"reports_to": lead_profile.email},
        fields=["name", "user"],
        limit_page_length=page_len,
        start=start
    )
    print(employees,'!!!!!!!!!!!!!!!!!!!!!!')
    print([(emp.name) for emp in employees])
    return [[emp.name] for emp in employees if emp.user]





SICK_LEAVE_LIMIT = 10
CASUAL_LEAVE_LIMIT = 10

@frappe.whitelist()
def get_remaining_leaves(user, leave_type):
    used = frappe.db.count('Leave Request', {
        'owner': user,
        'leave_type': leave_type,
        'docstatus': 1  
    })

    limit = SICK_LEAVE_LIMIT if leave_type == "Sick Leave" else CASUAL_LEAVE_LIMIT
    return {"remaining": max(0, limit - used)}


@frappe.whitelist()
def add_task_comment(docname, comment_text):
    doc = frappe.get_doc("Tasks", docname)
    doc.add_comment("Comment", comment_text)
    return "Comment added successfully"