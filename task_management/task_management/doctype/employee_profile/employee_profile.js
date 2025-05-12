// to show only the team lesad names nthe reports to feild
frappe.ui.form.on('Employee Profile', {
    onload: function(frm) {
        frm.set_query('reports_to', function() {
            return {
                query: 'frappe.core.doctype.user.user.user_query',
                filters: {
                    role: 'Team Lead'
                }
            };
        });
    }
});

// frappe.ui.form.on('Employee Profile', {
//     refresh(frm) {
//         if (!frm.is_new()) {
//             frm.set_df_property('password', 'read_only', 1);
//         }
//     }
// });

// only show the is manager o ony teh administsetor
frappe.ui.form.on('Employee Profile', {
    refresh: function(frm) {
        if (frappe.session.user !== "Administrator") {
            frm.set_df_property('is_hr_manager', 'hidden', 1);
        }
    }
});

frappe.ui.form.on('Employee Profile', {
    refresh: function(frm) {
        toggle_fields(frm);
    },
    reports_to: function(frm) {
        toggle_fields(frm);
    },
    is_team_lead: function(frm) {
        toggle_fields(frm);
    }
});

function toggle_fields(frm) {
    if (frm.doc.reports_to) {
        frm.set_df_property('is_team_lead', 'read_only', 1);
        frm.set_df_property('is_team_lead', 'description', 'You cannot be a team lead if you report to someone.');
    } else {
        frm.set_df_property('is_team_lead', 'read_only', 0);
        frm.set_df_property('is_team_lead', 'description', '');
    }

    if (frm.doc.is_team_lead) {
        frm.set_df_property('reports_to', 'read_only', 1);
        frm.set_df_property('reports_to', 'description', 'Team Leads do not report to anyone.');
    } else {
        frm.set_df_property('reports_to', 'read_only', 0);
        frm.set_df_property('reports_to', 'description', '');
    }
}
