var doc_fields=[];
var full_doc_fields=[];
var avail_conditions=[];

dashboard.DashboardOptions = Class.extend({
    init: function(opts, show_dialog) {
        $.extend(this, opts);
        this.show_dialog = show_dialog;
        
        this.module=opts.module;        

        let d = this.item;
        // if (opts.dashboard_type == 'counter')
        //     this.counter = 1;
        // else if(opts.dashboard_type=='graph')
        //     this.graph=1;
        // else if(opts.dashboard_type=='list')
        //     this.list=1;

        this.query='';
        this.user_permission=false;
        this.query_conditions=[];        
        this.number_fields=[];
        this.select_fields=opts.select_fields;
        this.cdt=opts.cdt;
        this.cdn=opts.cdn;
        this.setup();
    },

    setup: function() {
        this.make_dialog();
        this.on_close_dialog();
    },

    make_dialog: function() {
        var me = this;

        this.data = this.oldest ? this.oldest : [];
        let title = "New Condition";
        let fields=this.get_condition_field();
        this.dialog = new frappe.ui.Dialog({
            title: title,
            fields: fields
        });        

        this.dialog.set_primary_action(__('Insert'), function() {
            me.values = me.dialog.get_values();
            me.set_items();
            me.dialog.hide();
        });
        if(me.conditions.length>0){
            $(me.conditions).each(function(k,v){
                me.dialog.fields_dict.conditions.df.data.push({
                    'condition_field': v.field,
                    'cond': v.condition,
                    'value': v.value
                });
            });
            me.dialog.fields_dict.conditions.grid.refresh();
        }
        
        this.dialog.show();
        // this.dialog.$wrapper.find('.grid-remove-rows').hide();
        // this.dialog.$wrapper.find('.modal-dialog').css("width", "80%");
    },

    on_close_dialog: function() {
        this.dialog.get_close_btn().on('click', () => {
            this.on_close && this.on_close(this.item);
        });
    },

    set_items: function() {
        var me = this;
        var values=me.dialog.get_values();
        var newrow = frappe.model.add_child(me.frm.doc,"Dashboard Conditions", "conditions");
        if(values.conditions){
            $(values.conditions).each(function(k,v){
                frappe.model.set_value(newrow.doctype,newrow.name,'field',v.condition_field)
                frappe.model.set_value(newrow.doctype,newrow.name,'condition',v.cond)
                frappe.model.set_value(newrow.doctype,newrow.name,'value',v.value)
                frappe.model.set_value(newrow.doctype,newrow.name,'condition_type',me.cdt)
                frappe.model.set_value(newrow.doctype,newrow.name,'condition_for',me.cdn)
            })
            me.frm.refresh_field("conditions");
        }
    },
    
    get_counter_fields: function() {
        var me = this;
        return [
            {
                fieldtype: "Data",
                fieldname: "display_text",
                label: "Text To Display",
                reqd: 1
            },
            {
                fieldtype: "Check",
                fieldname: "check_permissions",
                label: "Check For Permissions"
            },
            { fieldname:'cl1',fieldtype:'Column Break'},
            {
                fieldtype: "Select",
                fieldname: "counter_type",
                options: ["Count", "Sum"],
                label: "Counter Type",
                reqd: 1,
                onchange:function(e){
                    let val=this.get_value();
                    me.counter_type=val;
                    if(val=='Count'){
                        me.query='select count(*) as count from `tab'+me.reference_doctype+'`';
                        get_preview(me);
                    }                                  
                }
            },
            {
                fieldtype: "Select",
                fieldname: "referred_field",
                label: "Pick Column",
                depends_on: "eval:{{doc.counter_type=='Sum'}}",
                onchange:function(e){
                    let val=this.get_value();
                    me.referred_field=val;
                    me.query='select sum('+val+') as sum from `tab'+me.reference_doctype+'`';
                    get_preview(me);
                }
            },
            {
                fieldtype: "Select",
                fieldname: "date_range",
                options: ["Daily", "Weekly", "Monthly", "All Time"],
                label: "Date Range",
                default: "All Time",
                onchange:function(e){
                    let val=this.get_value();
                    me.date_range=val;
                    if(me.date_range){
                        if(me.query.indexOf('where')==-1)
                            me.query=me.query
                        else
                            me.query=me.query.split('where')[0]
                        if(me.date_range=='Daily')
                            me.query+=' where CAST(creation as DATE)=CURDATE()';
                        else if(me.date_range=='Weekly')
                            me.query+=' where creation BETWEEN CURDATE() and DATE_SUB(CURDATE(), INTERVAL 7 DAY)';
                        else if(me.date_range=='Monthly')
                            me.query+=' where MONTH(CURDATE())=MONTH(creation)';
                    }
                    add_conditions(me);
                }
            }
        ]
    },

    get_graph_fields:function(){
        var me=this;
        return [
            {
                fieldtype: "Data",
                fieldname: "graph_title",
                label: "Graph Title",
                reqd: 1
            },
            { fieldtype:'Column Break',fieldname:'cl2'},
            {
                fieldtype: "Select",
                fieldname: "graph_type",
                label: "Graph Type",
                options:["Bar","Line","Pie"],
                reqd: 1
            },
            {
                label:"Date Field",
                fieldname:"date_field",
                fieldtype:"Select",
                reqd:1
            },
            { fieldname:'sl56', fieldtype:'Section Break'},
            {
                fieldname:'new_dataset',
                fieldtype:'HTML'
            }
        ]
    },

    get_data_sets:function(){
        var me=this;
        return [
            {fieldname:'sb1',fieldtype:'Section Break', label:'DataSet & Condition'},
            {
                fieldname:"datasets",
                fieldtype:"Table",
                // depends_on:"eval:doc.reference_doctype",
                fields:[
                    {
                        fieldtype:"Select",
                        fieldname:"dataset_field",
                        label:"Select Field",
                        in_list_view:1,
                        options:me.number_fields,
                        onchange:function(e){
                            this.grid_row.on_grid_fields_dict.color.set_value('');
                            this.grid_row.on_grid_fields_dict.label.set_value('');
                            make_datasets(me);
                        }
                    },                    
                    {
                        fieldtype:"Data",
                        fieldname:"label",
                        label:"Label",
                        in_list_view:1,
                        onchange:function(e){
                            var data_set=this.grid_row.on_grid_fields_dict.dataset_field.get_value();
                            var label=this.grid_row.on_grid_fields_dict.label.get_value();
                            if(data_set && label)
                                make_datasets(me);
                        }
                    },
                    {
                        fieldtype:"Color",
                        fieldname:"color",
                        label:"Graph Color",
                        in_list_view:1,
                        onchange:function(e){
                            make_datasets(me);
                        }
                    }
                ],
                in_place_edit: true,
                data: this.data,
                get_data: function() {
                    return this.data;
                }
            },
            { fieldname:'cl3', fieldtype:'Column Break' },
            {
                fieldname:"dataset_condition",
                fieldtype:"Table",
                // depends_on:"eval:doc.reference_doctype",
                fields:[
                    {
                        fieldtype:"Select",
                        fieldname:"dataset_fieldc",
                        label:"Dataset Field",
                        in_list_view:1,
                        options:me.number_fields,
                        onchange:function(e){
                            // make_datasets(me);
                        }
                    },                    
                    {
                        fieldtype:"Select",
                        fieldname:"condition_field",
                        label:"Select Field",
                        in_list_view:1,
                        options:doc_fields,
                        onchange:function(e){
                            this.grid_row.on_grid_fields_dict.cond.set_value('');
                            this.grid_row.on_grid_fields_dict.value.set_value('');
                        }
                    },
                    {
                        fieldtype:"Select",
                        fieldname:"cond",
                        label:"Condition",
                        in_list_view:1,
                        options:avail_conditions,
                        onchange:function(e){
                            let val=this.get_value();
                        }
                    },
                    {
                        fieldtype:"Data",
                        fieldname:"value",
                        label:"Value",
                        in_list_view:1,
                        onchange:function(e){
                            var cond_f=this.grid_row.on_grid_fields_dict.condition_field.get_value();
                            var cond=this.grid_row.on_grid_fields_dict.cond.get_value();
                            var val=this.grid_row.on_grid_fields_dict.value.get_value();
                            if(cond && val && cond_f)
                                add_conditions(me);
                        }
                    }
                ],
                in_place_edit: true,
                data: this.data,
                get_data: function() {
                    return this.data;
                }
            }
        ]
    },

    get_list_fields:function(){
        var me=this;
        return[
            {
                fieldname:'data_count',
                fieldtype:'Int',
                label:'No. of Data',
            },
            {
                fieldtype:'Data',
                reqd:1,
                fieldname:'title',
                label:'Title'
            },
            {
                fieldname:'check_permissions',
                fieldtype:'Check',
                label:'Check Permissions'
            },
            { fieldtype:'Column Break',fieldname:'cl009' },            
            {
                fieldtype:'Select',
                fieldname:'display_type',
                options:["Full Width","Half Width"],
                label:"Display Type"
            },            
            {
                fieldname:'sl45',
                fieldtype:'Section Break',
                label:"Conditions"
            }
        ]
    },

    get_condition_field:function(){
        var me = this;
        return [        
            {
                fieldname:"conditions",
                fieldtype:"Table",
                // depends_on:"eval:doc.reference_doctype",
                fields:[
                    {
                        fieldtype:"Select",
                        fieldname:"condition_field",
                        label:"Select Field",
                        in_list_view:1,
                        options:me.select_fields,
                        onchange:function(e){
                            
                        }
                    },                    
                    {
                        fieldtype:"Select",
                        fieldname:"cond",
                        label:"Condition",
                        in_list_view:1,
                        options:["Equals","Like","Not Equals","Not Like",">","<",">=","<="],
                        onchange:function(e){
                            let val=this.get_value();
                        }
                    },
                    {
                        fieldtype:"Data",
                        fieldname:"value",
                        label:"Value",
                        in_list_view:1,
                        onchange:function(e){
                            // var cond_f=this.grid_row.on_grid_fields_dict.condition_field.get_value();
                            // var cond=this.grid_row.on_grid_fields_dict.cond.get_value();
                            // var val=this.grid_row.on_grid_fields_dict.value.get_value();
                            // if(cond && val && cond_f)
                            //     add_conditions(me);
                        }
                    }
                ],
                in_place_edit: true,
                data: this.data,
                get_data: function() {                    
                    return this.data;
                }
            }
        ]
    },

    get_preview_fields:function(){
        var me = this;
        return [
            {
                fieldtype: "Section Break",
                fieldname: "sl1",
                label:"Preview"
            },
            {
                fieldtype: "HTML",
                fieldname: "preview"
            }
        ]
    },

    set_counter_item:function(){
        var me=this;
        frappe.model.set_value(me.item.doctype, me.item.name, "reference_doctype", me.values.reference_doctype)
        frappe.model.set_value(me.item.doctype, me.item.name, "counter_type", me.values.counter_type)
        frappe.model.set_value(me.item.doctype, me.item.name, "display_text", me.values.display_text)
        frappe.model.set_value(me.item.doctype, me.item.name, "query_field", me.query)
        frappe.model.set_value(me.item.doctype, me.item.name, "check_user_permissions", me.values.check_permissions)
    },
    
    get_conditions:function(){
        avail_conditions=["Equals","Like","Not Equals","Not Like",">","<",">=","<="];
    },
});
var get_preview=function(e){
    var me=e;
    let values=me.dialog.get_values();
    if(me.query!=''){
        frappe.call({
            method:'dashboard.dashboard.doctype.dashboards.dashboards.get_preview_data',
            args:{
                query:me.query
            },
            callback:function(data){
                if(data.message){
                    if(me.counter){
                        $(data.message).each(function(k,v){
                            var html='<div class="row"><div class="col-xs-12 col-sm-4 col-md-4">\
                            <div style="border: 1px solid #ccc;padding: 10px 15px;"><div>\
                            <h5 style="font-size: 25px;">'+v+'</h5></div><div><p>'+values.display_text
                            html+='</p></div></div></div></div>';
                            $('.modal').find('div[data-fieldname="preview"]').html(html)
                        })
                    }
                }
            }
        })
    }
}
var add_conditions=function(e){
    var me=e;
    let values=me.dialog.get_values();
    if(values.conditions){
        $(values.conditions).each(function(k,v){
            if(me.query.indexOf('where')>-1) me.query+=' and'; else me.query+=' where';
            var current_field=full_doc_fields.find(obj=>obj.label==v.condition_field)
            me.query+=' '+current_field.fieldname
            if(v.cond=='Equals') 
                me.query+='="'+v.value+'"';
            else if(v.cond=='Like')
                me.query+=' like "%'+v.value+'%"';
            else if(v.cond=='Not Equals')
                me.query+='!='+v.value+'"';
            else if(v.cond=='Not Like')
                me.query+=' not like "%'+v.value+'%"';
            else me.query+=v.cond+'"'+v.value+'"';
        })
    }
    if(me.graph)
        get_graph_preview(me);
    else
        get_preview(me);
}
var make_datasets=function(e){
    var me=e;
    var values=me.dialog.get_values();
}
var get_graph_preview=function(e){
    var me=e;
    if(me.query_conditions.length>0){
        frappe.call({
            method:'dashboard.dashboard.doctype.dashboards.dashboards.get_graph_query',
            args:{
                query:query_conditions
            },
            callback:function(data){

            }
        })
    }
}