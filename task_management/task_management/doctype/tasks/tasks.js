// get employees assigned to team leads
frappe.ui.form.on('Tasks', {
    onload: function(frm) {
        frm.set_query('assigned_to', () => {
            return {
                query: "task_management.api.get_team_members"
            };
        });
    }
});


frappe.ui.form.on('Tasks', {
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
                }
            }
        });
    }
});


// comment box
frappe.ui.form.on('Tasks', {
    refresh: function (frm) {
        setTimeout(() => {
            frm.timeline.wrapper.find('.timeline-comment-box').hide();
        }, 300);

        frm.clear_custom_buttons();

        frappe.call({
            method: 'frappe.client.get_value',
            args: {
                doctype: 'Employee Profile',
                filters: { user: frappe.session.user },
                fieldname: 'name'
            },
            callback: function (r) {
                if (r.message) {
                    frm.add_custom_button(__('💬 Add Comment'), function () {
                        let d = new frappe.ui.Dialog({
                            title: 'Add a Comment',
                            fields: [
                                {
                                    label: 'Comment',
                                    fieldname: 'comment',
                                    fieldtype: 'Small Text',
                                    reqd: 1
                                }
                            ],
                            primary_action_label: 'Submit',
                            primary_action(values) {
                                frappe.call({
                                    method: 'frappe.desk.form.utils.add_comment',
                                    args: {
                                        reference_doctype: frm.doctype,
                                        reference_name: frm.docname,
                                        content: values.comment,
                                        comment_email: frappe.session.user,
                                        comment_by: frappe.session.user
                                    },
                                    callback: function () {
                                        d.hide();
                                        frappe.msgprint(__('Comment added successfully'));
                                        frm.reload_doc();  // Reload to show comment
                                    }
                                });
                            }
                        });
                        d.show();
                    });
                }
            }
        });
    }
});
