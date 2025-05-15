import frappe

def get_permission_query_conditions(user, doctype):
    conditions = []


    employee = frappe.db.get_value("Employee Profile", {"user": user}, "name")


    user_roles = frappe.get_roles(user)
    
    if "HR Manager" in user_roles:
        return ""  
    elif "Team Lead" in user_roles:
        conditions.append(f"`tabEmployee Profile`.`reports_to` = '{user}'")
        conditions.append(f"`tabEmployee Profile`.`user` = '{user}'")
        return " OR ".join(conditions)
    else:
        return f"`tabEmployee Profile`.`user` = '{user}'"
