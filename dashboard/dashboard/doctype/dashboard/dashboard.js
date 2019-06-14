// Copyright (c) 2018, info@valiantsystems.com and contributors
// For license information, please see license.txt

frappe.ui.form.on('Dashboard', {
	refresh: function(frm) {
		
	},
	module_dashboard:function(frm){
		if(frm.doc.module_dashboard){
			frm.set_df_property('module','reqd',1)
		}else{
			frm.set_df_property('module','reqd',0)
		}
	},
	enable_counter:function(frm){
		if(frm.doc.enable_counter){
			frm.set_df_property('counters','reqd',1)
		}else{
			frm.set_df_property('counters','reqd',0)
		}
	},
	enable_graph:function(frm){
		if(frm.doc.enable_graph){
			frm.set_df_property('graphs','reqd',1)
		}else{
			frm.set_df_property('graphs','reqd',0)
		}
	},
	enable_listings:function(frm){
		if(frm.doc.enable_listings){
			frm.set_df_property('listing','reqd',1)
		}else{
			frm.doc.set_df_property('listing','reqd',0)
		}
	},module:function(frm){
		if(frm.doc.module){
			frm.set_query('doctype','counters',function(doc,cdt,cdn){
				return{
					'filters':{
						'module':frm.doc.module
					}
				}
			})
			frm.set_query('doctype','graphs',function(doc,cdt,cdn){
				return{
					'filters':{
						'module':frm.doc.module
					}
				}
			})
			frm.set_query('doctype','listing',function(doc,cdt,cdn){
				return{
					'filters':{
						'module':frm.doc.module
					}
				}
			})
		}
	}
});
frappe.ui.form.on("Dashboard Counters List", {
	reference_doctype: function(frm, cdt, cdn) {
    	var item = frappe.get_doc(cdt, cdn);
    	console.log(item)
        // if(item.doctype){
        // 	frappe.call({
        // 		method:'dashboard.dashboard.doctype.dashboard.get_doc_fields',
        // 		args:{
        // 			doctype:item.doctype
        // 		},
        // 		callback:function(data){
        // 			console.log(data.message)
        // 			frappe.meta.get_docfield("Dashboard Graph", "data1_field",cur_frm.docname).options = data.message;
        // 			frappe.meta.get_docfield("Dashboard Graph", "data2_field",cur_frm.docname).options = data.message;
        // 		}
        // 	})
        // }
    },
    counters_add:function(frm,cdt,cdn){
    	console.log(1)
    }
});
frappe.ui.form.on("Dashboard Listing", {
    reference_doctype: function(frm, cdt, cdn) {
    	var item = frappe.get_doc(cdt, cdn);
    	console.log(item)
        // if(frm.doc.doctype){
        // 	frappe.call({
        // 		method:'dashboard.dashboard.doctype.dashboard.get_doc_fields',
        // 		args:{
        // 			doctype:item.doctype
        // 		},
        // 		callback:function(data){
        // 			console.log(data.message)
        // 			frappe.meta.get_docfield("Dashboard Graph", "date1_field",cur_frm.docname).options = data.message;
        // 			frappe.meta.get_docfield("Dashboard Graph", "date2_field",cur_frm.docname).options = data.message;
        // 		}
        // 	})
        // }
    }
})
frappe.ui.form.on("Dashboard Graph", "doctype", function(frm, cdt, cdn) {
    var item = frappe.get_doc(cdt, cdn);
    // console.log(item.whatsapp_number.length)
    // if (item.whatsapp_number.length != 10 && item.whatsapp_number.length != 0) {
    //     frappe.model.set_value(cdt, cdn, "whatsapp_number", '');
    //     frappe.throw('Please enter 10 digit Whatsapp Number for member ' + item.member_name + ' in Event Managing Team')
    // }
    console.log(item)
});