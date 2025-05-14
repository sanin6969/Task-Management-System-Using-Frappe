// automatically enters emp value
frappe.ui.form.on('Leave Request', {
    // onload: function(frm) {
    //     if (frm.is_new()) {
    //         frappe.call({
    //             method: "task_management.api.get_employee_profile",
    //             callback: function(r) {
    //                 if (r.message) {
    //                     frm.set_value("employee", r.message);
    //                 }
    //             }
    //         });
    //     }
    // },
    from_date: function(frm) {
        calculate_leave_days(frm);
    },
    to_date: function(frm) {
        calculate_leave_days(frm);
    },
    leave_type: function(frm) {
        get_remaining_leaves(frm);
    }
});


function calculate_leave_days(frm) {
    if (frm.doc.from_date && frm.doc.to_date) {
        const from = frappe.datetime.str_to_obj(frm.doc.from_date);
        const to = frappe.datetime.str_to_obj(frm.doc.to_date);
        if (to >= from) {
            const days = frappe.datetime.get_diff(frm.doc.to_date, frm.doc.from_date) + 1;
            frm.set_value('leave_days', days);
        } else {
            frm.set_value('leave_days', 0);
        }
    }
}

function get_remaining_leaves(frm) {
    if (frm.doc.leave_type) {
        frappe.call({
            method: 'task_management.api.get_remaining_leaves',
            args: {
                user: frm.doc.owner,
                leave_type: frm.doc.leave_type
            },
            callback: function(r) {
                if (r.message) {
                    frm.set_value('remaining_leaves', r.message.remaining);
                }
            }
        });
    }
}
