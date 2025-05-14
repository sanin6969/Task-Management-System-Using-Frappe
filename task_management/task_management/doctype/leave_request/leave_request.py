# Copyright (c) 2025, Sxnin and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LeaveRequest(Document):
    def before_validate(self):
        self.employee = frappe.session.user

    def validate(self):
        used = frappe.db.count('Leave Request', {
            'owner': self.owner,
            'leave_type': self.leave_type,
            'docstatus': 1
        })

        leave_days = float(self.leave_days)
        limit = 10 if self.leave_type == "Sick Leave" else 10

        if used + leave_days > limit:
            frappe.throw(
                f"You have exceeded your {self.leave_type} limit. Only {limit - used} days left."
            )


