frappe.ui.form.on('Tasks', {
        onload: function(frm) {
            frm.set_query('assigned_to', () => {
                return {
                    query: "task_management.api.get_team_members"
                };
            });
        },
        
    refresh: async function(frm) {
        const is_team_lead = await frappe.user.has_role("Team Lead");
        const is_employee = await frappe.user.has_role("Employee");
        const is_hr_manager = await frappe.user.has_role("HR Manager");

        if (is_team_lead) {
            frm.page.add_inner_button('Mark Assigned', function () {
                frm.set_value("status", "Assigned ");
            }, 'Change Status');

        }
        if (is_employee && !is_team_lead && !is_hr_manager) {
            frm.page.add_inner_button('Mark In Progress', function () {
                frm.set_value("status", "In Progress");
            }, 'Change Status');

            frm.page.add_inner_button('Mark Completed', function () {
                frm.set_value("status", "Completed");
            }, 'Change Status');

            frm.add_custom_button("Add Comment", () => {
                const d = new frappe.ui.Dialog({
                    title: "Add Comment",
                    fields: [
                        {
                            label: 'Comment',
                            fieldname: 'comment_text',
                            fieldtype: 'Small Text',
                            reqd: true
                        }
                    ],
                    primary_action_label: 'Add',
                    primary_action(values) {
                        frappe.call({
                            method: "task_management.api.add_task_comment",
                            args: {
                                docname: frm.doc.name,
                                comment_text: values.comment_text
                            },
                            callback: function(r) {
                                frappe.msgprint(r.message);
                                d.hide();
                                frm.reload_doc();
                            }
                        });
                    }
                });
                d.show();
            });
        }
    }

});




