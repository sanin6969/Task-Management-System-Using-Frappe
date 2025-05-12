// automatically enters emp value
frappe.ui.form.on('Leave Request', {
    onload: function(frm) {
        if (frm.is_new()) {
            frappe.call({
                method: "task_management.api.get_employee_profile",
                callback: function(r) {
                    if (r.message) {
                        frm.set_value("employee", r.message);
                    }
                }
            });
        }
    }
});

