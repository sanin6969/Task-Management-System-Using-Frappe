import frappe

def get_permission_query_conditions(user, doctype):
    if "HR Manager" in frappe.get_roles(user):
        return "`tabLeave Request`.`workflow_state` != 'Draft'" 
    employee_profile = frappe.db.get_value("Employee Profile", {"user": user}, "email")
    # print(employee_profile,'empmpppprrrrrrrrooooooffffffiiilllleeeeeee')
    if not employee_profile:
        return None  
    
    if "Team Lead" in frappe.get_roles(user):
        team_members = frappe.get_all(
            "Employee Profile", 
            filters={"reports_to": user},  
            pluck="email"
        )
        allowed_employees = team_members + [employee_profile]
        # print(allowed_employees,'allowed_employees')
        

        
        allowed_str = ", ".join(f"'{emp}'" for emp in allowed_employees)
        # print(allowed_str,'aaaaaallowwweeddddddd str')
        return (f"`tabLeave Request`.`employee` IN ({allowed_str})")
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    # return f"`tabLeave Request`.`employee` = '{employee_profile}'" 
 
 
#  AND "
#                 f"`tabLeave Request`.`status` IN ('Pending Team Lead Approval', 'Approved')