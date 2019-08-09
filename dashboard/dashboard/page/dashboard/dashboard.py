from __future__ import unicode_literals
import frappe
import json
from frappe.model.document import Document
from frappe.share import add
from frappe import _, throw
from frappe.utils import getdate, add_months, get_last_day, nowdate
from frappe.utils import flt
from datetime import datetime, timedelta
from frappe.utils import now_datetime

@frappe.whitelist()
def get_dashboard_items(name):
	dashboard=frappe.db.get_all('Dashboards',filters={'name':name},fields=['*'])
	lists=[]
	if dashboard:
		dashboard_items=frappe.db.get_all('Dashboard Counters List',fields=['type','dashboard_item','column_width','no_of_counters'],
		filters={'parent':dashboard[0].name},order_by='idx')
		if dashboard_items:
			for item in dashboard_items:
				if item.type=='Counter':
					counters_list=frappe.db.get_all('Dashboard Items',filters={'type':'Counter','group':item.dashboard_item},fields=['*'],order_by='display_order')
					counter_data=get_counters_new(counters_list)
					if counter_data:
						item.counter_list=counter_data
					if item.no_of_counters==6:
						item.counter_class='col-md-2 col-sm-4 col-xs-6'
					elif item.no_of_counters==5:
						item.counter_class='col-md-2 cols-5 col-sm-4 col-xs-6'
					elif item.no_of_counters==4:
						item.counter_class='col-md-3 col-sm-3 col-xs-6'
					elif item.no_of_counters==3:
						item.counter_class='col-md-4 col-sm-4 col-xs-6'
					elif item.no_of_counters==2:
						item.counter_class='col-md-6 col-sm-6 col-xs-6'
					elif item.no_of_counters==1:
						item.counter_class='col-md-12 col-sm-12 col-xs-12'
				else:
					graph=frappe.db.get_all('Dashboard Items',filters={'type':item.type,'name':item.dashboard_item},fields=['*'])
					if item.type=='Graph':
						graph_data=get_graph_new(graph)
						if graph_data:
							item.graph=graph_data[0]
					elif item.type=='Table':
						table_data=get_table_new(graph)
						if table_data:
							item.table=table_data[0]
		return dashboard_items

@frappe.whitelist()
def get_counters_new(counters_list):
	counter=[]
	if counters_list:
		today=getdate(nowdate())		
		for item in counters_list:
			dash=frappe.get_doc('Dashboard Items',item.name)
			ignore_permissions=False if dash.check_user_permissions else True
			filters=[]
			res=frappe.db.sql('''select count(*) as count from `tab{doctype}`'''.format(doctype=dash.reference_doctype),as_dict=1)			
			if dash.conditions:
				for c in dash.conditions:
					filters.append(get_conditions(c))
			if dash.date_range=='Daily':	
				st_start_date=datetime(year=today.year,day=today.day,month=today.month)				
				fil1=["creation",">=",st_start_date]
				fil2=["creation","<=",st_start_date]
				filters.append(fil1)
			elif dash.date_range=='Monthly':
				st_date=datetime(year=today.year,day=01,month=today.month)
				next_month = st_date.replace(day=28) + timedelta(days=4)
				ed_date=next_month - timedelta(days=next_month.day)
				filt1=["creation",">=",st_date]
				filt2=["creation","<=",ed_date]
				filters.append(filt1)
				filters.append(filt2)
			elif dash.date_range=='Weekly':
				start = today - timedelta(days=today.weekday())
				end = start + timedelta(days=6)
				filt1=["creation",">=",start]						
				filt2=["creation","<=",end]				
				filters.append(filt1)
				filters.append(filt2)
			result=frappe.get_list(dash.reference_doctype,fields=['*'],filters=filters,ignore_permissions=ignore_permissions,limit_page_length=res[0].count)									
			if dash.counter_type=='Count':
				counter.append({'title':dash.display_text,'count':len(result),'css':dash.css_style,'name':dash.name})
			else:
				total=sum(res[dash.referred_field] for res in result)
				counter.append({'title':dash.display_text,'count':("%0.2f" % total),'css':dash.css_style,'name':dash.name})	
	return counter

@frappe.whitelist()
def get_graph_new(graph_list):
	months=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
	today=getdate(nowdate())
	chartslist=[]
	if frappe.db.get_value('DocType','Catalog Settings'):
		default_currency=frappe.db.get_single_value('Catalog Settings','default_currency')
		currency_symbol=frappe.get_value('Currency',default_currency,'symbol')
	elif frappe.db.get_value('DocType','Global Defaults'):
		default_currency=frappe.db.get_single_value('Global Defaults','default_currency')
		currency_symbol=frappe.get_value('Currency',default_currency,'symbol')
	else:
		currency_symbol=None
	if graph_list:
		for item in graph_list:
			chart=frappe.get_doc('Dashboard Items',item.name)
			res=frappe.db.sql('''select count(*) as count from `tab{doctype}`'''.format(doctype=chart.reference_doctype),as_dict=1)		
			color=[]
			datasets=[]			
			docfields=frappe.get_meta(chart.reference_doctype).get("fields")
			currency=False
			ignore_permissions=False if chart.check_user_permissions else True
			if chart.datasets:
				for it in chart.datasets:
					d_val=[]
					month=0
					while month<12:
						month=month+1
						st_date=datetime(year=today.year,day=01,month=month)
						next_month = st_date.replace(day=28) + timedelta(days=4)
						ed_date=next_month - timedelta(days=next_month.day)						
						filters_g=[]
						if chart.conditions:
							for c in chart.conditions:
								if c.condition_for==it.name:
									filters_g.append(get_conditions(c))
						filt1=["creation",">=",st_date]
						filt2=["creation","<=",ed_date]
						filters_g.append(filt1)
						filters_g.append(filt2)
						result=frappe.get_list(chart.reference_doctype,fields=['*'],filters=filters_g,ignore_permissions=ignore_permissions,limit_page_length=res[0].count)
						if it.fieldname!='Name':
							docs=next((x.fieldtype for x in docfields if x.fieldname==it.fieldname),None)
						else:
							docs='Link'
						if docs=='Int' or docs=='Float' or docs=='Currency':
							total=sum(res[it.fieldname] for res in result)
							d_val.append(("%0.2f" % total))
						else:
							d_val.append(len(result))
						if docs=='Currency':
							currency=True
					datasets.append({'values':d_val,'name':it.label,'chartType':it.chart_type.lower()})
					color.append(it.color)
				ids=item.name.replace(' ','').lower()
				chartslist.append({'label':months,'dataset':datasets,'title':chart.display_text,'id':ids,'color':color,'type':chart.graph_type.lower(),'size':item.display_type,'dot_size':item.dot_size,'space_ratio':item.space_ratio,'hide_dots':item.hide_dots,'hide_line':item.hide_line,'heat_line':item.heat_line,'values_over_points':item.values_over_points,'navigate':item.navigate,'height':item.chart_height,'currency':currency,'currency_symbol':currency_symbol})
			else:
				filters=[]
				docs=next((x.fieldname for x in docfields if x.label==chart.date_fields),None)
				query='''select distinct {date_fields} from `tab{doctype}` '''.format(date_fields=docs,doctype=chart.reference_doctype)
				distinct_records = frappe.db.sql(query,as_dict=1)
				results=[]				
				for dis in distinct_records:
					filters=[]
					if chart.conditions:
						for c in chart.conditions:
							if c.condition_for==it.name:
								filters.append(get_conditions(c))
					fil=[docs,'=',dis.status]
					filters.append(fil)
					response=frappe.get_list(chart.reference_doctype,filters=filters,fields=[docs],ignore_permissions=ignore_permissions,limit_page_length=res[0].count)
					if chart.value_type=='Count':
						results.append({'label':dis.status,'value':len(response)})
					else:
						total=sum(res[docs] for res in response)
						results.append({'label':dis,'value':total})
				label=[res['label'] for res in results]
				value=[res['value'] for res in results]
				ids=item.name.replace(' ','').lower()
				datasets=[]
				datasets.append({'values':value,'name':'Test','chartType':chart.graph_type.lower()})
				colors=[]
				if chart.color:
					colors.append(chart.color.split('\n'))
				chartslist.append({'label':label,'dataset':datasets,'title':chart.display_text,'id':ids,'color':colors,'type':chart.graph_type.lower()})
	return chartslist

@frappe.whitelist()
def get_table_new(table_list):
	listing=[]
	today=getdate(nowdate())
	now=datetime.now()
	if table_list:
		if frappe.db.get_value('DocType','Catalog Settings'):
			default_currency=frappe.db.get_single_value('Catalog Settings','default_currency')
			currency=frappe.get_value('Currency',default_currency,'symbol')
		elif frappe.db.get_value('DocType','Global Defaults'):
			default_currency=frappe.db.get_single_value('Global Defaults','default_currency')
			currency=frappe.get_value('Currency',default_currency,'symbol')
		else:
			currency=None		
		for item in table_list:
			table=frappe.get_doc('Dashboard Items',item.name)
			ignore_permissions=False if table.check_user_permissions else True
			filters=[]
			if table.conditions:
				for c in table.conditions:
					filters.append(get_conditions(c))				
			fields_list=frappe.db.get_all('Table Fields',filters={'parent':table.name},fields=['*'],order_by='idx',limit_page_length=100)
			fields_arr=[]
			fields=[]
			docfields=frappe.get_meta(table.reference_doctype).get("fields")
			for fi in fields_list:				
				if fi.fieldname=='name':
					docs=table.reference_doctype
					ftype='Link'
				else:
					docs=next((x.options for x in docfields if x.fieldname==fi.fieldname))
				new_fld={'id':fi.fieldname,'name':fi.display_name,'resizable':fi.resizable,'sortable':fi.sortable,'focusable':fi.focusable,'editable':0}
				if fi.format:
					format_data='(value)=>{'
					format_data+='{format_data}'.format(format_data=fi.format)
					format_data+='}'
					new_fld['format']=format_data
				else:
					ftype=next((x.fieldtype for x in docfields if x.fieldname==fi.fieldname),None)					
					if ftype=='Link':
						new_fld['format']='(value)=>{return `<a href="#Form/'+docs+'/${value}">${value}</a>`}'
					elif ftype=='Currency':
						if currency:
							new_fld['format']='(value)=>{return `'+currency+' ${value}`}'
						new_fld['align']='right'
					elif ftype=='Float' or ftype=='Int':
						new_fld['align']='right'
					new_fld['fieldtype']=ftype
				fields.append(fi.fieldname)
				fields_arr.append(new_fld)
			res=frappe.get_list(table.reference_doctype,fields=fields,filters=filters,limit_page_length=table.no_of_data,order_by='modified desc',ignore_permissions=ignore_permissions)
			ids=item.name.replace(' ','').lower()
			listing.append({'data':res,'fields':fields_arr,'doctype':table.reference_doctype,'title':table.display_text,'size':item.display_type,'id':ids})
	return listing

@frappe.whitelist()
def get_conditions(conditions):
	symbol=conditions.condition_symbol
	if symbol.find('&lt;')!=-1:
		symbol=symbol.replace('&lt;','<')
	elif symbol.find('&gt;')!=-1:
		symbol=symbol.replace('&gt;','>')
	fil=[conditions.fieldname,symbol]
	if conditions.condition_symbol=='not in' or conditions.condition_symbol=='in':
		fil.append(conditions.value.split('\n'))
	else:
		if conditions.fieldtype=='Date' and conditions.value=='Today':
			fil.append(today)
		elif conditions.fieldtype=='Datetime' and conditions.value=='Today':
			now=datetime.now()
			fil.append(now)
		else:
			fil.append(conditions.value)
	return fil

@frappe.whitelist()
def get_counter_info(counter):
	counter_info=frappe.db.get_all('Dashboard Items',filters={'name':counter},fields=['reference_doctype','name','date_range'])
	if counter_info:
		conditions=frappe.db.get_all('Dashboard Conditions',filters={'parent':counter_info[0].name},fields=['fieldname','condition_symbol','value'])
		filters={}
		if conditions:
			for item in conditions:
				filters[item.fieldname]=[item.condition_symbol,item.value]
		return {'doctype':counter_info[0].reference_doctype,'filters':filters}