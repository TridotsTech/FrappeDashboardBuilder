// Copyright (c) 2018, info@valiantsystems.com and contributors
// For license information, please see license.txt
frappe.provide('dashboard')
frappe.ui.form.on('Dashboards', {
    refresh: function(frm) {
        // $(".grid-add-row").hide();
        // $('.grid-add-multiple-rows').removeClass('hide');
        // $('.grid-add-multiple-rows').text('Add Row')
    },
    refer_module: function(frm) {
        if (frm.refer_module) {
            frm.set_df_property('module', 'reqd', 1)
        } else {
            frm.set_df_property('module', 'reqd', 0)
        }
    },
    module: function(frm) {
        if (frm.doc.module) {
            frm.set_query('reference_doctype', 'counters', function(doc, cdt, cdn) {
                return {
                    'filters': {
                        'module': frm.doc.module
                    }
                }
            })
            frm.set_query('reference_doctype', 'graph', function(doc, cdt, cdn) {
                return {
                    'filters': {
                        'module': frm.doc.module
                    }
                }
            })
            frm.set_query('reference_doctype', 'listing', function(doc, cdt, cdn) {
                return {
                    'filters': {
                        'module': frm.doc.module
                    }
                }
            })
        }
    }
});
var counter_fields = []
frappe.ui.form.on("Dashboard Counters List", {
    // view_properties: function(frm, cdt, cdn) {
    //     var item = frappe.get_doc(cdt, cdn);
    //     if (item.reference_doctype) {
    //         frappe.route_options = { doc_type: item.reference_doctype };
    //         frappe.set_route("Form", "Customize Form");
    //     } else {
    //         frappe.msgprint('Please select doctype', 'Alert')
    //     }
    // },
    // reference_doctype: function(frm, cdt, cdn) {
    //     var item = locals[cdt][cdn];
    //     if (item.reference_doctype) {
    //         frappe.call({
    //             method: 'dashboard.dashboard.doctype.dashboards.dashboards.get_doc_fields',
    //             args: {
    //                 doctype: item.reference_doctype
    //             },
    //             callback: function(data) {
    //                 if (data.message) {
    //                     // show_counter_popup(data.message)
    //                 }
    //             }
    //         })
    //     }
    // },
    // counters_add: function(frm, cdt, cdn) {
    //     var item = locals[cdt][cdn];        
    //     frappe.require("assets/dashboard/js/dashboard_options.js", function() {
    //         new dashboard.DashboardOptions({
    //             module: frm.doc.module,
    //             item: item,
    //             dashboard_type:'counter'
    //         });
    //     });
    // }
    type:function(frm,cdt,cdn){
        let items=locals[cdt][cdn];
        if(items.type){
            let link_doctype=''
            if(items.type=='Counter')
                link_doctype='Dashboard Groups'
            else
                link_doctype='Dashboard Items'
            frappe.model.set_value(cdt,cdn,'link_field_type',link_doctype)
        }
    }
});
frappe.ui.form.on("Dashboard Listing", {
    // view_properties: function(frm, cdt, cdn) {
    //     var item = frappe.get_doc(cdt, cdn);
    //     if (item.reference_doctype) {
    //         frappe.route_options = { doc_type: item.reference_doctype };
    //         frappe.set_route("Form", "Customize Form");
    //     } else {
    //         frappe.msgprint('Please select doctype', 'Alert')
    //     }
    // },
    // view_properties_child: function(frm, cdt, cdn) {
    //     var item = frappe.get_doc(cdt, cdn);
    //     if (item.child_doctype) {
    //         frappe.route_options = { doc_type: item.child_doctype };
    //         frappe.set_route("Form", "Customize Form");
    //     } else {
    //         frappe.msgprint('Please select doctype', 'Alert')
    //     }
    // },
    // listing_add:function(frm,cdt,cdn){
    //     var item = locals[cdt][cdn];
    //     frappe.require("assets/dashboard/js/dashboard_options.js", function() {
    //         new dashboard.DashboardOptions({
    //             module: frm.doc.module,
    //             item: item,
    //             dashboard_type:'list'
    //         });
    //     });
    // }    
})
frappe.ui.form.on("Dashboard Graph List", {
    view_properties_h: function(frm, cdt, cdn) {
        var item = frappe.get_doc(cdt, cdn);
        if (item.reference_doctype) {
            frappe.route_options = { doc_type: item.reference_doctype };
            frappe.set_route("Form", "Customize Form");
        } else {
            frappe.msgprint('Please select doctype', 'Alert')
        }
    },
    view_prperties_v: function(frm, cdt, cdn) {
        var item = frappe.get_doc(cdt, cdn);
        if (item.reference_doctype) {
            frappe.route_options = { doc_type: item.reference_doctype };
            frappe.set_route("Form", "Customize Form");
        } else {
            frappe.msgprint('Please select doctype', 'Alert')
        }
    },
    graph_add:function(frm,cdt,cdn){
        var item = locals[cdt][cdn];
        frappe.require("assets/dashboard/js/dashboard_options.js", function() {
            new dashboard.DashboardOptions({
                module: frm.doc.module,
                item: item,
                dashboard_type:'graph'
            });
        });
    }
})


var show_counter_popup = function(data) {

}

var show_dialog = function(title, fields) {
    var dialog = new frappe.ui.Dialog({
        title: title,
        fields: fields
    });    
    if(this.show_dialog){
        dialog.fields_dict.conditions.df.data.push({
            'value':'test'
        });
        dialog.fields_dict.conditions.grid.refresh();
    }
    dialog.show();    
    dialog.$wrapper.find('.modal-dialog').css("width", "80%");
}
var conditions=''
var add_new_counter = function(frm,item) {
    var title = "Add New Counter";
    var fields = [
        {
            fieldname: "reference_doctype",
            label: "Reference",
            fieldtype: "Link",
            options: "DocType",
            reqd: 1,
            get_query: function() {
                return {
                    filters: { module: frm.doc.module },
                    query: 'dashboard.dashboard.doctype.dashboards.dashboards.get_doctypes'
                }
            },
            onchange: function(e) {
                let val = this.get_value();
                let d = this;
                if (val) {
                    frappe.call({
                        method: 'dashboard.dashboard.doctype.dashboards.dashboards.get_doc_fields',
                        args: {
                            doctype: val
                        },
                        callback: function(data) {
                            if (data.message) {
                                counter_fields = data.message;
                                var options = '<option value=""></option>';
                                conditions='<option value=""></option>'
                                $(counter_fields).each(function(k, v) {
                                    if (v.fieldtype == 'Float' || v.fieldtype == 'Int' || v.fieldtype == 'Currency') {
                                        options += '<option value="' + v.fieldname + '">' + v.label + '</option>'
                                    }
                                    conditions+='<options value="'+v.fieldname+'" data-fieldtype="'+v.fieldtype+'">'+v.label+'</option>';
                                })
                                $('.modal').find('select[data-fieldname="referred_field"]').html(options)
                            }
                        }
                    })
                }
            }
        },
        {
            fieldtype: "Data",
            fieldname: "display_text",
            label: "Text To Display",
            reqd: 1
        },
        {
            fieldtype: "Select",
            fieldname: "counter_type",
            options: ["Count", "Sum"],
            label: "Counter Type",
            reqd: 1
        },
        {
            fieldtype: "Select",
            fieldname: "referred_field",
            label: "Pick Column",
            depends_on: "eval:{{doc.counter_type=='Sum'}}"
        },
        {
            fieldtype: "Select",
            fieldname: "date_range",
            options: ["Daily", "Weekly", "Monthly", "All Time"],
            label: "Date Range",
            default: "All Time"
        },
        {
            fieldtype: "Check",
            fieldname: "check_permissions",
            label: "Check For Permissions"
        }        
    ]
    // fields=fields.concat(condition_table())
    // console.log(fields)
    fields=fields.concat(get_preview_fields())
    show_dialog(title,fields)
}
var get_preview_fields=function(){
    return [
        {
            fieldtype: "Column Break",
            fieldname: "cl1"
        },
        {
            fieldtype: "HTML",
            fieldname: "preview"
        }
    ]
}
var condition_table=function(){
    return [
        // {fieldtype:'Section Break', label: __('Condition')},
        {
            fieldname:"conditions",
            fieldtype:"Table",
            depends_on:"eval:doc.reference_doctype",
            fields:[
                {
                    fieldtype:"Select",
                    fieldname:"condition_field",
                    label:"Select Field",
                    in_list_view:1,
                    options:'',
                    onchange:function(e){
                        let val=this.get_value()
                    }
                },
                {
                    fieldtype:"Select",
                    fieldname:"cond",
                    label:"Condition",
                    in_list_view:1,
                    options:'',
                    onchange:function(e){
                        let val=this.get_value();
                    }
                },
                {
                    fieldtype:"Data",
                    fieldname:"value",
                    label:"Value",
                    in_list_view:1
                }
            ]
        }
    ]
}