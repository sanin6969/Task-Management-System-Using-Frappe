# Copyright (c) 2025, Sxnin and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LeaveRequest(Document):
    
    def before_validate(self):
        if not self.employee:
            self.employee = frappe.session.user
        
    def validate(self):
        leave_days = float(self.leave_days)
        employee = frappe.get_doc("Employee Profile", {"user": self.owner})

        if self.leave_type == "Sick Leave":
            if employee.sick_leave_remaining < leave_days:
                frappe.throw(f"Not enough sick leave. You only have {round(employee.sick_leave_remaining)} days left.")
        elif self.leave_type == "Casual Leave":
            if employee.casual_leave_remaining < leave_days:
                frappe.throw(f"Not enough casual leave. You only have {round(employee.casual_leave_remaining)} days left.")

    def on_submit(self):
        if self.docstatus == 1:
            # print("submitting the leaaaave reqeusrstttttt")
            employee = frappe.get_doc("Employee Profile", {"user": self.owner})
            leave_days = float(self.leave_days)

            if self.leave_type == "Sick Leave":
                employee.sick_leave_remaining -= leave_days
            elif self.leave_type == "Casual Leave":
                employee.casual_leave_remaining -= leave_days

            employee.save()

