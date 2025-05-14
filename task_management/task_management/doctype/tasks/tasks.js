frappe.ui.form.on('Tasks', {
        onload: function(frm) {
            frm.set_query('assigned_to', () => {
                return {
                    query: "task_management.api.get_team_members"
                };
            });
        },
        
    refresh: function(frm) {
        frappe.call({
            method: 'frappe.client.get_value',
            args: {
                doctype: 'Employee Profile',
                filters: { user: frappe.session.user },
                fieldname: 'name'
            },
            callback: function(response) {
                const is_employee = !!response.message;
                const is_team_lead = frappe.user.has_role("Team Lead");
    
                if (is_employee && !is_team_lead) {
                    frm.set_df_property('created_date', 'read_only', 1);
                    frm.set_df_property('assigned_to', 'read_only', 1);
                    frm.set_df_property('status', 'read_only', 1);
                }
            }
        });
        if (frappe.user.has_role("Employee") &&
            !frappe.user.has_role("Team Lead") &&
            !frappe.user.has_role("HR Manager")) {

            frm.page.add_inner_button('Mark In Progress', function () {
                frm.set_value("status", "In Progress");
            }, 'Change Status');

            frm.page.add_inner_button('Mark Completed', function () {
                frm.set_value("status", "Completed");
            }, 'Change Status');

            frm.add_custom_button("Add Comment", () => {
                const d = new frappe.ui.Dialog({
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




