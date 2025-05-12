frappe.ui.form.on('Tasks', {
    onload: function(frm) {
        frm.set_query('assigned_to', () => {
            return {
                query: "task_management.api.get_team_members"
            };
        });
    }
});
