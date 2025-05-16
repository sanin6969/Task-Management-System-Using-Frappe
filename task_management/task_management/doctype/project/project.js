frappe.ui.form.on('Project', {
    onload: function(frm) {
        const role = frappe.user_roles;

        if (role.includes('HR Manager')) {
            frm.set_df_property('task', 'hidden', 1);
        }
        if (role.includes('Team Lead')) {
            frm.set_value('team_lead', frappe.session.user);
            frm.set_df_property('team_lead', 'read_only', 1);
        }
    },
    refresh: async function(frm) {
        highlight_task(frm);
        const is_team_lead = await frappe.user.has_role("Team Lead");
        if (is_team_lead){
            frm.page.add_inner_button('Mark Completed', function () {
                frm.set_value("status", "Completed");
            }, 'Change Status');
        }
    },
    task_on_form_rendered: function(frm, cdt, cdn) {
        highlight_task(frm);
    }

});



function highlight_task(frm) {
    const today = frappe.datetime.get_today();

    frm.fields_dict.task.grid.grid_rows.forEach(row => {
        const doc = row.doc;
        const status = (doc.status).toLowerCase();
        const due_date = doc.due_date;

        let color = "";

        if (status === "completed") {
            color = "green";
            // if (due_date === today) {
            //     color = "red"; 
            // }
        } else if (due_date === today && ["not started", "started"].includes(status)) {
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
