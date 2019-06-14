// Copyright (c) 2018, info@valiantsystems.com and contributors
// For license information, please see license.txt

frappe.ui.form.on('Dashboard Detail View', {
	refresh: function(frm) {
// frappe.call({
// 			method: 'frappe.custom.doctype.custom_field.custom_field.get_fields_label',
// 			args: { doctype: "Payment Entry"},
// 			callback: function(r, rt) {
// 				console.log(r)
// 				set_field_options('insert_after', r.message);
// 				// var fieldnames = $.map(r.message, function(v) { return v.value; });

// 				// if(insert_after==null || !in_list(fieldnames, insert_after)) {
// 				// 	insert_after = fieldnames[-1];
// 				// }

// 				// frm.set_value('insert_after', insert_after);
// 			}
// 		});
		frm.set_query("title", "counters", function(doc, cdt, cdn) {
			return {
				"filters": {
					"type": ["in","Counter"],
				}
			};
		});

	},
    
});
