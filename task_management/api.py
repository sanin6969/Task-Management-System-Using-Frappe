import frappe
from frappe import _

@frappe.whitelist()
def get_team_members(doctype, txt, searchfield, start, page_len, filters):
    user = frappe.session.user

    if "Team Lead" not in frappe.get_roles(user):
        frappe.throw(_("You are not authorized to assign tasks"))

    lead_profile = frappe.get_doc("Employee Profile", {"user": user})
    
    # print(lead_profile.email,'////////////')
    
    employees = frappe.get_all("Employee Profile",
        filters={"reports_to": lead_profile.email},
        fields=["name", "user","email"],
        limit_page_length=page_len,
        start=start
    )
    # print(employees,'!!!!!!!!!!!!!!!!!!!!!!')
    # print([(emp.email,emp.user,emp.name) for emp in employees])
    return [(emp.name, emp.user) for emp in employees if emp.user]


@frappe.whitelist()
def get_employee_profile():
	user = frappe.session.user
	return frappe.get_value("Employee Profile", {"user": user}, "name")