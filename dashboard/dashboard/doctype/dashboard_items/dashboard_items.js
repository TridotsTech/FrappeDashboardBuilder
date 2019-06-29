// Copyright (c) 2018, info@valiantsystems.com and contributors
// For license information, please see license.txt
var docfields = [];
var condition_field = [];
var date_fields = [];
var table_fields=[];
frappe.provide('dashboard')
frappe.ui.form.on('Dashboard Items', {
    refresh: function(frm) {
        if (frm.doc.reference_doctype) {
            get_doc_fields(frm, frm.doc.reference_doctype)
            get_child_docs(frm, frm.doc.reference_doctype)
            if (frm.doc.reference_child_doc_name) {
                get_child_doc_fields(frm, frm.doc.reference_child_doc_name)
            }
        }
        docfields = [];
        condition_field = [];
        date_fields = [];
    },
    reference_doctype: function(frm) {
        if (frm.doc.reference_doctype) {
            get_doc_fields(frm, frm.doc.reference_doctype)
            get_child_docs(frm, frm.doc.reference_doctype)
        }
    },
    reference_child_doc_name: function(frm) {
        if (frm.doc.reference_child_doc_name) {
            get_child_doc_fields(frm, frm.doc.reference_child_doc_name)
        }
    },
    before_save: function(frm) {
    },
    graph_type:function(frm){
        if(frm.doc.graph_type){
            if(frm.doc.graph_type=='Pie' || frm.doc.graph_type=='Percentage')
                frm.set_df_property("date_fields", "options", condition_field);
            else
                frm.set_df_property("date_fields", "options", date_fields);
        }
    }
});

frappe.ui.form.on('Dashboard Conditions', {
    field: function(frm, cdt, cdn) {
        var item = locals[cdt][cdn];
        if (item.field) {
            var fields = docfields.find(obj => obj.label.trim() == item.field.trim());
            if(fields){
                frappe.model.set_value(cdt, cdn, "fieldname", fields.fieldname);
            }else{
                let field=get_field_def(item.field)
                if(field)
                    frappe.model.set_value(cdt, cdn, "fieldname", field.fieldname);
            }            
        }
    }
});

frappe.ui.form.on('Table Fields', {
    field: function(frm, cdt, cdn) {
        var item = locals[cdt][cdn];
        if (item.field) {
            var fields = docfields.find(obj => obj.label == item.field);
            if(fields){
                frappe.model.set_value(cdt, cdn, "fieldname", fields.fieldname);
                frappe.model.set_value(cdt, cdn, "fieldtype", fields.fieldtype);                
            }else{
                let field=get_field_def(item.field)
                if(field){
                    frappe.model.set_value(cdt, cdn, "fieldname", field.fieldname);
                    frappe.model.set_value(cdt, cdn, "fieldtype", field.fieldtype);
                }
                
            }
            frappe.model.set_value(cdt, cdn, "display_name", item.field);           
        }
    }
});

frappe.ui.form.on('Graph Dataset', {
    condition: function(frm, cdt, cdn) {
        var item = locals[cdt][cdn];
        if (item.__islocal) {
            frappe.msgprint('Please save the document and continue to edit')
        } else {
            get_all_conditions(frm, cdt, cdn);
        }
    },
    field: function(frm, cdt, cdn) {
        var item = locals[cdt][cdn];
        if (item.field) {
            var fields = docfields.find(obj => obj.label == item.field);
            if(fields){
                frappe.model.set_value(cdt, cdn, "fieldname", fields.fieldname);
            }else{
                let field=get_field_def(item.field)
                if(field)
                    frappe.model.set_value(cdt, cdn, "fieldname", field.fieldname);
            }           
        }
    }
})

var get_doc_fields = function(frm, doctype) {
    frappe.call({
        method: 'dashboard.dashboard.doctype.dashboard_detail_view.dashboard_detail_view.get_fields_label',
        args: { doctype: doctype },
        callback: function(data, rt) {
            if (data.message) {
                condition_field = [];
                var numeric_fields = [];
                docfields = [];
                $(data.message).each(function(k, v) {
                    if ((v.fieldtype != 'Section Break' && v.fieldtype != 'Column Break')) {
                        condition_field.push(v.label)
                    }
                    if ((v.fieldtype == 'Int' || v.fieldtype == 'Float' || v.fieldtype == 'Currency') && v.hidden == 0 && v.fieldname!='docstatus')
                        numeric_fields.push(v.label)
                    if (v.fieldtype == 'Date' || v.fieldtype == 'Datetime')
                        date_fields.push(v.label)
                    if((v.fieldtype != 'Section Break' && v.fieldtype != 'Column Break' && v.fieldtype !='Table')){
                        docfields.push(v);
                    }
                    if ((v.fieldtype != 'Section Break' && v.fieldtype != 'Column Break' && v.fieldtype != 'Table' && v.fieldtype != 'HTML') && v.hidden == 0)
                        table_fields.push(v.label);
                });
                frappe.meta.get_docfield('Dashboard Conditions', 'field', cur_frm.doc.name).options = condition_field;
                frappe.meta.get_docfield('Table Fields', 'field', cur_frm.doc.name).options = table_fields;
                frm.set_df_property("value_fields", "options", numeric_fields);
                if(frm.doc.graph_type=='Pie' || frm.doc.graph_type=='Percentage')
                    frm.set_df_property("date_fields", "options", condition_field);
                else
                    frm.set_df_property("date_fields", "options", date_fields);
                frappe.meta.get_docfield('Graph Dataset', 'field', cur_frm.doc.name).options = condition_field;
                get_fields(frm, docfields)
            }
        }
    })
}
var get_child_docs = function(frm, doctype) {
    frappe.call({
        method: 'dashboard.dashboard.doctype.dashboard_detail_view.dashboard_detail_view.get_fields_label_with_options',
        args: { doctype: doctype },
        callback: function(data, rt) {
            if (data.message) {
                condition_field = [];
                var numeric_fields = [];
                docfields = data.message;
                $(data.message).each(function(k, v) {
                    if ((v.fieldtype == 'Table')) {
                        condition_field.push(v.options)
                    }
                })
                frm.set_df_property('reference_child_doc_name', 'options', condition_field.join("\n"));
            }
        }
    })
}

var get_child_doc_fields = function(frm, doctype) {
    if (frm.doc.reference_child_doc_name) {
        frappe.call({
            method: 'dashboard.dashboard.doctype.dashboard_detail_view.dashboard_detail_view.get_fields_labels_list',
            args: { doctype: doctype },
            callback: function(data, rt) {
                if (data.message) {
                    condition_field = [];
                    var numeric_fields = [];
                    docfields = data.message;
                    $(data.message).each(function(k, v) {

                        if ((v.fieldtype != 'Section Break' && v.fieldtype != 'Column Break')) {
                            condition_field.push(v.label)
                        }
                        if ((v.fieldtype == 'Int' || v.fieldtype == 'Float' || v.fieldtype == 'Currency') && v.hidden == 0)
                            numeric_fields.push(v.label)
                        if (v.fieldtype == 'Date' || v.fieldtype == 'DateTime')
                            date_fields.push(v.label)
                    })

                    frappe.meta.get_docfield('Dashboard Ctable Conditions', 'field', cur_frm.doc.name).options = condition_field;

                    // frm.set_df_property("date_fields", "options", date_fields);
                    // frappe.meta.get_docfield('Graph Dataset','field',cur_frm.doc.name).options=numeric_fields;
                    // get_fields(frm,docfields)
                }
            }
        })
    }
}
var condition_dialog = function(frm, cdt, cdn, conditions) {
    frappe.require("assets/dashboard/js/dashboard_options.js", function() {
        new dashboard.DashboardOptions({
            select_fields: condition_field,
            cdt: cdt,
            cdn: cdn,
            all_fields: docfields,
            frm: frm,
            conditions: conditions
        });
    });
}
var get_all_conditions = function(frm, cdt, cdn) {
    var conditions = [];
    $(frm.doc.conditions).each(function(k, v) {
        if (v.condition_type == cdt && v.condition_for == cdn) {
            conditions.push(v);
        }
    })
    condition_dialog(frm, cdt, cdn, conditions);
}

var get_fields = function(frm, docfields) {
    var html = '<div id="fields_to_specify"><div class="clearfix"><label class="control-label">Select Fields To Display</label></div>'
    $(docfields).each(function(k, v) {
        if ((v.fieldtype != 'Section Break' && v.fieldtype != 'Column Break') && v.hidden == 0)
            html += '<div class="col-md-6"><div class="checkbox"><label><span class="input-area"><input\
             type="checkbox" autocomplete="off" class="input-with-feedback" name="ftd" label="' + v.label + '"\
              value="' + v.fieldname + '" /></span><span class="disp-area" style="display:none"><i \
              class="octicon octicon-check" style="margin-right: 3px;"></i></span><span \
              class="label-area small">' + v.label + '</span></label><p class="help-box \
              small text-muted"></p></div></div>';
    });
    html += '</div>';
    if (frm.doc.fields_to_specify) {
        fields = frm.doc.fields_to_specify.split(',');
        $(fields).each(function(k, v) {
            if (v) {
                $("#fields_to_specify input[value='" + v + "']").attr('checked', true);
            }
        })
    }
}

var get_field_def=function(field){
    let field_details={};
    if(field=='Name'){
        field_details.fieldname='name';
        field_details.fieldtype='Link';
    }else if(field=='Created On'){
        field_details.fieldname='creation';
        field_details.fieldtype='Datetime';
    }else if(field=='Modified On'){
        field_details.fieldname='modified';
        ffield_details.ieldtype='Datetime';
    }else if(field=='Created By'){
        field_details.fieldname='owner';
        field_details.fieldtype='Link';
    }else if(field=='Modified By'){
        field_details.fieldname='modified_by';
        field_details.fieldtype='Link';
    }else if(field=='Document Status'){
        field_details.fieldname='docstatus';
        field_details.fieldtype='Int';
    }
    return field_details
}