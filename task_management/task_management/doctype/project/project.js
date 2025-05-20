frappe.ui.form.on('Project', {
    onload:async function(frm) {
        const is_team_lead = await frappe.user.has_role("Team Lead");
        const is_employee = await frappe.user.has_role("Employee");
        const is_hr_manager = await frappe.user.has_role("HR Manager");
        if (is_hr_manager) {
            frm.set_df_property('task', 'read_only', 1);
        }
        if (is_team_lead) {
            frm.set_value('team_lead', frappe.session.user);
            frm.set_df_property('team_lead', 'read_only', 1);
        }
        if (is_employee && !is_team_lead && !is_hr_manager) {
            frm.set_df_property('team_lead', 'read_only', 1);
            frm.set_df_property('Team_lead', 'read_only', 1);
            frm.set_df_property('start_date', 'read_only', 1);
            frm.set_df_property('end_date', 'read_only', 1);
            frm.set_df_property('task', 'read_only', 1);
            frm.set_df_property('project_name', 'read_only', 1);

        }
    },
    refresh: async function(frm) {
        highlight_task(frm);
        const is_team_lead = await frappe.user.has_role("Team Lead");
        if (is_team_lead){
            mark_completed(frm)
        }
    },
    task_on_form_rendered: function(frm, cdt, cdn) {
        highlight_task(frm);
    }

});


function mark_completed(frm) {
    frm.page.add_inner_button('Mark Completed', function () {
        frappe.call({
            method: "task_management.api.mark_project_completed",
            args: {
                project_name: frm.doc.name
            },
            callback: function (r) {
                if (!r.message) return;

                if (r.message.status === "completed") {
                    frm.set_value("status", "Completed");
                    frm.save();
                    frappe.msgprint("Project marked as completed.");
                } else if (r.message.status === "incomplete") {
                    const task_list = r.message.incomplete_tasks.map(task =>
                        `Task: ${task.task_name} - Assigned to: ${task.assigned_to || 'N/A'}`
                    ).join('<br>');

                    frappe.confirm(
                        `The following tasks are not completed:<br>${task_list}<br><br>Do you want to notify the assigned users?`,
                        function () {
                            frappe.call({
                                method: "task_management.api.send_task_reminders",
                                args: {
                                    project_name: frm.doc.name
                                },
                                callback: function () {
                                    frappe.msgprint("Notification sent to assigned users.");
                                }
                            });
                        },
                        function () {
                            frappe.msgprint("Action cancelled.");
                        }
                    );
                }
            }
        });
    }, 'Change Status');
    
}
function highlight_task(frm) {
    const today = frappe.datetime.get_today();

    frm.fields_dict.task.grid.grid_rows.forEach(row => {
        const doc = row.doc;
        const status = (doc.status).toLowerCase();
        const due_date = doc.due_date;

        let color = "";

        if (status === "completed") {
            color = "green";
        } else if (
            (due_date === today && ["not started", "started"].includes(status)) ||
            status === "overdue"
        ) {
            color = "red";
        }

        if (color) {
            $(row.row).css({
                "background-color": color === "red" ? "#ff9999" : "#66cc99"  
            });
        } else {
            $(row.row).css("background-color", "");
        }
    });
}
