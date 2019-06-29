// import { Chart } from "frappe-charts";

frappe.pages['dashboard'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Dashboard',
        single_column: true
    });
    $('#page-dashboard .page-content').find('.layout-main').append(frappe.render_template("dashboard"));
    $('#page-dashboard .page-content').find('.layout-main').prepend('<div class="formlist"></div>')
}
frappe.pages['dashboard'].refresh = function(wrapper) {
    let routes=frappe.get_route()
    let module='';
    let name='';
    if(routes.length==3){
        module=routes[1];
        name=routes[2];
        $('#page-dashboard .page-title .title-text').text(module + ' Dashboard')
        frappe.breadcrumbs.add(module)
    }else{
        name=routes[1];
        $('#page-dashboard .page-title .title-text').text('Dashboard')
    }
    if(routes.length==1){
        frappe.set_route('/')
    }else{
        // $('#counters').html('')
        // $('#charts').html('')
        // $('#listing').html('')
        // get_counters(module,name)
        // get_chart(module,name)
        // get_listings(module,name)
        get_dashboard_items(name)
    }
}
var get_counters = function(module,name) {
    frappe.call({
        method: 'dashboard.dashboard.page.dashboard.dashboard.get_dashboard_counter',
        args: {
            module: module,
            name:name
        },
        callback: function(data) {
            if (data.message) {
                if (data.message.length > 0) {
                    $('#counters').html(frappe.render_template("dashboard_counter", { content: data.message }));
                }
            }
        }
    })
}
var get_chart = function(module,name) {
    frappe.call({
        method: 'dashboard.dashboard.page.dashboard.dashboard.get_dashboard_chart',
        args: {
            module: module,
            name:name
        },
        callback: function(data) {
            if (data.message) {
                $('#charts').html(frappe.render_template("dashboard_chart", { content: data.message }));
                var chart_count = 1;
                for (var i = 0; i < data.message.length; i++) {
                    var id = "#" + data.message[i].id;
                    var label = data.message[i].label;
                    var title = data.message[i].title;
                    var datasets = data.message[i].dataset;
                    var color = data.message[i].color;
                    var type = data.message[i].type;
                    draw_graph(id, title, label, datasets, color, type)
                }
            }
        }
    })
}
var get_listings = function(module,name) {
    frappe.call({
        method: 'dashboard.dashboard.page.dashboard.dashboard.get_dashboard_listing',
        args: {
            module: module,
            name:name
        },
        callback: function(data) {
            if (data.message) {
                if (data.message.length > 0) {
                    $('#listing').html(frappe.render_template("dashboard_listing", { content: data.message }));
                    $(data.message).each(function(k, v) {
                        $(v.fields).each(function(i,j){
                            if(j.format){
                                j.format=(eval(j.format))
                            }
                        })
                        construct_table(v.fields, v.data, v.id)
                    })
                }
            }
        }
    })
}

var draw_graph = function(id, title, label, datasets, color, type, graph) {
    var data = {
        datasets: datasets,
        labels: label
    }
    var args = {
        title: title,
        type: type,
        height: 200,
        colors: color,
        parent: id,
        data: data
    }
    if (type == 'mixed charts')
        type = 'axis-mixed'
    
    let chart = new frappeCharts.Chart(id, {
        title: title,
        data: data,
        type: type,
        height: graph.height ? graph.height : 240,
        colors: color,
        barOptions: {
            spaceRatio: graph.space_ratio ? graph.space_ratio : 0.2
        },
        lineOptions: {
            dotSize: graph.dot_size ? graph.dot_size : 4,
            hideDots:graph.hide_dots ? graph.hide_dots : 0,
            hideLine:graph.hide_line ? graph.hide_line : 0,
            heatline:graph.heat_line ? graph.heat_line :0
        },
        valuesOverPoints:graph.values_over_points ? graph.values_over_points : 0,
        isNavigable:graph.navigate ? graph.navigate : 0
    })
}

var construct_table = function(fields, values, id) {    
    let datatable = new DataTable('#' + id, {
        columns: fields,
        data: values,
        layout:'fluid',
        noDataMessage:'Sorry! No records found.'  
    });
    $('#'+id).find('.dt-row-header .dt-cell__content').each(function(){
        var txt=$(this).text().replace(/\_/g,' ')
        $(this).text(txt)
    })
    // let ex=new DataTable('#example1',{
    //     columns:[{
    //         name:'Status',
    //         id:'status',
    //         format:(value)=>{
    //             if(value=='Success'){
    //                 return value.bold()
    //             }else{
    //                 return value
    //             }
    //         }
    //     }],
    //     data: [
    //         ['Success'],
    //         ['Failure']
    //     ]
    // })
}

var get_dashboard_items=function(name){
    frappe.call({
        method: 'dashboard.dashboard.page.dashboard.dashboard.get_dashboard_items',
        args: {
            name:name
        },
        callback: function(data) {
            if (data.message) {
                $('#page-dashboard .maindiv').html(frappe.render_template("dashboard_items", { content: data.message }));
                $(data.message).each(function(k, v) {
                    if(v.type=='Table'){
                        $(v.table.fields).each(function(i,j){
                            if(j.format){
                                j.format=(eval(j.format))
                            }
                        })
                        construct_table(v.table.fields, v.table.data, v.table.id)
                    }else if(v.type=="Graph"){
                        draw_graph('#'+v.graph.id, v.graph.title, v.graph.label, v.graph.dataset, v.graph.color, v.graph.type,v.graph)
                    }               
                })
            }
        }
    })
}