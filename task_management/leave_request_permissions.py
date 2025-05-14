import frappe

def get_permission_query_conditions(user, doctype):
    conditions = []

    employee = frappe.db.get_value("Employee Profile", {"user": user}, "email")
    employee_name =frappe.db.get_value("Employee Profile", {"user": user}, "name")
    print(employee,'employeeeeeee')
    print(employee_name,'employeeeeeee nnaaaaaaaammmmmmme')

    user_roles = frappe.get_roles(user)

    if "HR Manager" in user_roles:
        return ""  

    elif "Team Lead" in user_roles:
        # Fix: Compare reports_to to the employee name, not the user ID
        reports = frappe.get_all("Employee Profile", filters={"reports_to": employee}, pluck="name")
        print(reports,'rrrrrrrreeeeepppportsssss')
        # Include own leave requests
        allowed_employees = reports + [employee_name]
        print(allowed_employees,'aalllllllwwwwed')

        allowed_str = ", ".join(f"'{emp}'" for emp in allowed_employees)
        print(allowed_str,'aaaaaaaaaaalllllllllllllllo')
        return f"`tabLeave Request`.`employee` IN ({allowed_str})"

    else:
        # Regular employees can only see their own leave requests
        return f"`tabLeave Request`.`employee` = '{employee}'"
