from __future__ import unicode_literals
import frappe
import json
from frappe.model.document import Document
from frappe.share import add
from frappe import _, throw
from frappe.utils import getdate, add_months, get_last_day, nowdate
from frappe.utils import flt
from datetime import datetime, timedelta

@frappe.whitelist()
def get_dashboard_counter(name,module=None):
	# if module:
	# 	dashboard=frappe.db.get_all('Dashboards',filters={'module':module,'name'},fields=['*'])
	# 	if dashboard:
	# 		counterlist=get_counters(dashboard)
	# 		return counterlist
	# else:
	# 	dashboard=frappe.db.get_all('Dashboards',filters={'refer_module':0},fields=['*'])
	# 	if dashboard:
	# 		counterlist=get_counters(dashboard)
	# 		return counterlist
	dashboard=frappe.db.get_all('Dashboards',filters={'name':name},fields=['*'])
	if dashboard:
		counterlist=get_counters(dashboard)
		return counterlist

@frappe.whitelist()
def get_counter_data(dashboard):
	counter=[]
	counters=frappe.db.get_all('Dashboard Counters List',fields=['*'],filters={'parent':dashboard[0].name},order_by='idx')
	if counters:
		for item in counters:
			condition=''
			if item.condition:
				condition='where '+item.condition
			if item.condition and item.user_data and not "System Manager" in frappe.get_roles(frappe.session.user):
				condition+=' and '
			elif item.user_data and not item.condition and not "System Manager" in frappe.get_roles(frappe.session.user):
				condition+='where '
			if item.user_data and not "System Manager" in frappe.get_roles(frappe.session.user):
				if item.user_field:
					condition+='%s'% item.user_field
				else:
					condition+='owner'
				condition+="='%s'"% frappe.session.user
			if item.query_field:
				result=frappe.db.sql('''{query}'''.format(query=item.query_field),as_dict=1)
				if item.counter_type=='Count':
					counter.append({'title':item.display_text,'count':result[0].count,'size':dashboard[0].counter_count})
				else:
					counter.append({'title':item.display_text,'count':result[0].sum,'size':dashboard[0].counter_count})
			else:
				if item.counter_type=='Count':						
					result=frappe.db.sql('''select count(*) as count from `{table}` `{condition}`'''.format(condition=condition,table='tab' + item.reference_doctype),as_dict=1)
					counter.append({'title':item.display_text,'count':result[0].count,'size':dashboard[0].counter_count})
				else:
					result=frappe.db.sql('''select sum({refer_field}) as sum from `{table}` `{condition}`'''.format(refer_field=item.referred_field,condition=condition,table='tab'+item.reference_doctype),as_dict=1)
					if result[0].sum!=None:
						counter.append({'title':item.display_text,'count':result[0].sum,'size':dashboard[0].counter_count})
		return counter

@frappe.whitelist()
def get_dashboard_chart(name,module):
	# if module:
	# 	dashboard=frappe.db.get_all('Dashboards',filters={'module':module},fields=['*'])
	# 	if dashboard:
	# 		chartlist=get_charts(dashboard)
	# 		return chartlist
	# else:
	# 	dashboard=frappe.db.get_all('Dashboards',filters={'refer_module':0},fields=['*'])
	# 	if dashboard:
	# 		chartlist=get_charts(dashboard)
	# 		return chartlist
	dashboard=frappe.db.get_all('Dashboards',filters={'name':name},fields=['*'])
	if dashboard:
		chartlist=get_charts(dashboard)
		return chartlist

@frappe.whitelist()
def get_chart_data(dashboard):
	months=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
	year=getdate(nowdate()).year
	chartslist=[]
	charts=frappe.db.get_all('Dashboard Graph List',fields=['*'],filters={'parent':dashboard[0].name},order_by='idx')
	if charts:
		for item in charts:
			month=0
			color=[]
			color.append(item.graph_color)			
			condition=''
			data=[]
			if item.condition:
				condition='and '+item.condition
			if item.user_data and not "System Manager" in frappe.get_roles(frappe.session.user):
				condition+=' and '
				if item.user_field:
					condition+='%s'% item.user_field
				else:
					condition+='owner'
				condition+="='%s'"% frappe.session.user
			while month<12:
				datah=frappe.db.sql('''select sum(`{field}`) as sum from `{doctype}` where month(`{date_field}`)={month} and year(`{date_field}`)={year} {condition}'''.format(field=item.datav_field,doctype='tab'+item.reference_doctype,condition=condition,date_field=item.date_field,month=month,year=year),as_dict=1)
				if datah[0].sum!=None:
					data.append(datah[0].sum)
				else:
					data.append(0)
				month=month+1
			ids=item.parent+item.name
			chartslist.append({'label':months,'dataset':data,'title':item.graph_title,'id':ids,'color':color,'type':item.graph_type.lower(),'size':item.graph_display_type})
		return chartslist

@frappe.whitelist()
def get_dashboard_listing(name,module):
	# if module:
	# 	dashboard=frappe.db.get_all('Dashboards',filters={'module':module},fields=['*'])
	# 	if dashboard:
	# 		counterlist=get_listings(dashboard)
	# 		return counterlist
	# else:
	# 	dashboard=frappe.db.get_all('Dashboards',filters={'refer_module':0},fields=['*'])
	# 	if dashboard:
	# 		counterlist=get_listings(dashboard)
	# 		return counterlist
	dashboard=frappe.db.get_all('Dashboards',filters={'name':name},fields=['*'])
	if dashboard:
		counterlist=get_listings(dashboard)
		return counterlist

@frappe.whitelist()
def get_listing_data(dashboard):
	list_data=[]
	listing=frappe.db.get_all('Dashboard Listing',fields=['*'],filters={'parent':dashboard[0].name},order_by='idx')
	if listing:
		for item in listing:
			if item.use_custom_query:
				lists=frappe.db.sql('''{query}'''.format(query=item.custom_query))
				fields=[]
				if item.fields_list:
					f_list=item.fields_list.split(',')
					if f_list:
						for fl in f_list:
							fields.append({'field':fl})
				list_data.append({'data':lists,'fields':fields,'doctype':item.reference_doctype,'title':item.title,'size':item.display_type})
			else:
				parent_fields=''
				child_fields=''
				child_query=''
				p_c=''
				c_c=''
				FieldsList=[]
				p_field=item.fields_to_specify.split(',')
				for ls in p_field:
					if ls:
						parent_fields+='`tab%s`'% item.reference_doctype
						parent_fields+='.%s,'% ls
						if ls.find('_')!=-1:
							field=ls.replace('_',' ')
							FieldsList.append({'field':field})
						else:
							FieldsList.append({'field':ls})
				p_condition=item.condition.split(' and ')
				count=1
				if p_condition:
					for pc in p_condition:
						p_c+='`tab%s`'% item.reference_doctype
						p_c+='.%s'% pc.split('=')[0]
						p_c+="=%s "% pc.split('=')[1]												
						if count!=len(p_condition):
							p_c+="and "						
						count=count+1
				if item.user_data and not "System Manager" in frappe.get_roles(frappe.session.user):
					p_c+='`tab%s`'%item.reference_doctype
					if item.user_field:						
						p_c+='.%s='% item.user_field
					else:
						p_c+='.owner='
					p_c+="'%s'"% frappe.session.user
				if item.refer_child_table:	
					c_field=item.child_table_fields.split(',')
					for c in c_field:
						if c:
							child_fields+='`tab%s`'% item.child_doctype
							child_fields+='.%s,'% c
							if c.find('_')!=-1:
								field=c.replace('_',' ')
								FieldsList.append({'field':field})
							else:
								FieldsList.append({'field':c})
					if item.child_table_condition:
						if item.child_table_condition.find('and')!=-1:
							c_condition=item.child_table_condition.split(' and ')
						else:
							c_condition=item.child_table_condition
						if c_condition:
							for cc in c_condition:
								if cc.find('(select')!=-1:
									c_c+=' and %s'% cc
								else:	
									c_c+=' and `tab%s`'% item.child_doctype
									c_c+='.%s'% cc

					lists=frappe.db.sql('''select {parent_field} {child_field} from `{parent_doctype}`, `{child_doctype}` where `{parent_doctype}`.name=`{child_doctype}`.parent and {parent_condition} {child_condition} limit {limit}'''
							.format(parent_doctype='tab'+item.reference_doctype,child_doctype='tab'+item.child_doctype,parent_field=parent_fields[:-1],child_field=child_fields[:-1],parent_condition=p_c,child_condition=c_c[:-3],limit=item.data_count))
					list_data.append({'data':lists,'fields':FieldsList,'doctype':item.reference_doctype,'title':item.title,'size':item.display_type})
				else:
					# frappe.msgprint(frappe._('select {parent_field} from `{parent_doctype}` where {parent_condition} limit {limit}').format(parent_doctype='tab'+item.reference_doctype,parent_field=parent_fields[:-1],parent_condition=p_c,limit=item.data_count))
					lists=frappe.db.sql('''select {parent_field} from `{parent_doctype}` where {parent_condition} limit {limit}'''
							.format(parent_doctype='tab'+item.reference_doctype,parent_field=parent_fields[:-1],parent_condition=p_c,limit=item.data_count))
					list_data.append({'data':lists,'fields':FieldsList,'doctype':item.reference_doctype,'title':item.title,'size':item.display_type})
		return list_data

@frappe.whitelist()
def get_counters(dashboard):
	counter=[]
	counters=frappe.db.get_all('Dashboard Counters',filters={'parent':dashboard[0].name},fields=['*'],order_by='idx')
	if counters:
		today=getdate(nowdate())
		for item in counters:
			dash=frappe.get_doc('Dashboard Items',item.title)
			ignore_permissions=False if dash.check_user_permissions else True
			filters=[]
			res=frappe.db.sql('''select count(*) as count from `tab{doctype}`'''.format(doctype=dash.reference_doctype),as_dict=1)
			if dash.conditions:
				for c in dash.conditions:
					symbol=c.condition_symbol
					if symbol.find('&lt;')!=-1:
						symbol=symbol.replace('&lt;','<')
					elif symbol.find('&gt;')!=-1:
						symbol=symbol.replace('&gt;','>')
					fil=[c.fieldname,symbol]
					if c.condition_symbol=='not in' or c.condition_symbol=='in':
						fil.append(c.value.split('\n'))
					else:
						if c.fieldtype=='Date' and c.value=='Today':
							fil.append(today)
						elif c.fieldtype=='Datetime' and c.value=='Today':
							now=datetime.now()
							fil.append(now)
						else:
							fil.append(c.value)
					filters.append(fil)
			if dash.date_range=='Daily':
				fil1=["creation","=",today]
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
				counter.append({'title':dash.display_text,'count':len(result),'size':dashboard[0].counter_count,'css':dash.css_style})
			else:
				counter.append({'title':dash.display_text,'count':sum(res[dash.referred_field] for res in result),'size':dashboard[0].counter_count,'css':dash.css_style})					
			# else:				
			# 	if dash.query_field:
			# 		result=frappe.db.sql('''{query}'''.format(query=dash.query_field),as_dict=1)
			# 		if dash.counter_type=='Count':
			# 			counter.append({'title':dash.display_text,'count':result[0].count,'size':dashboard[0].counter_count,'css':dash.css_style})
			# 		else:
			# 			counter.append({'title':dash.display_text,'count':result[0].sum,'size':dashboard[0].counter_count,'css':dash.css_style})
	return counter

@frappe.whitelist()
def get_charts(dashboard):
	months=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
	today=getdate(nowdate())
	chartslist=[]	
	charts=frappe.db.get_all('Dashboard Graph',fields=['*'],filters={'parent':dashboard[0].name},order_by='idx')
	if charts:
		for item in charts:
			chart=frappe.get_doc('Dashboard Items',item.title)
			res=frappe.db.sql('''select count(*) as count from `tab{doctype}`'''.format(doctype=chart.reference_doctype),as_dict=1)		
			color=[]
			datasets=[]			
			docfields=frappe.get_meta(chart.reference_doctype).get("fields")
			if chart.datasets:
				for it in chart.datasets:
					d_val=[]
					month=0
					while month<12:
						month=month+1
						st_date=datetime(year=today.year,day=01,month=month)
						next_month = st_date.replace(day=28) + timedelta(days=4)
						ed_date=next_month - timedelta(days=next_month.day)
						ignore_permissions=False if chart.check_user_permissions else True
						filters_g=[]
						if chart.conditions:
							for c in chart.conditions:
								if c.condition_for==it.name:
									symbol=c.condition_symbol
									if symbol.find('&lt;')!=-1:
										symbol=symbol.replace('&lt;','<')
									elif symbol.find('&gt;')!=-1:
										symbol=symbol.replace('&gt;','>')
									fil=[c.fieldname,symbol]
									if c.condition_symbol=='not in' or c.condition_symbol=='in':
										fil.append(c.value.split('\n'))
									else:
										if c.fieldtype=='Date' and c.value=='Today':
											fil.append(today)
										elif c.fieldtype=='Datetime' and c.value=='Today':
											now=datetime.now()
											fil.append(now)
										else:
											fil.append(c.value)
									filters_g.append(fil)
						filt1=["creation",">=",st_date]
						filt2=["creation","<=",ed_date]
						filters_g.append(filt1)
						filters_g.append(filt2)
						result=frappe.get_list(chart.reference_doctype,fields=['*'],filters=filters_g,ignore_permissions=ignore_permissions,limit_page_length=res[0].count)
						# res=frappe.db.sql('''select sum({field}) as sum from `tab{doctype}`\
						#  where month(creation)={month} and year(creation)={year} {condition}'''
						#  .format(field=it.fieldname,doctype=chart.reference_doctype,month=month,year=today.year,condition=it.condition_query),as_dict=1)						
						# if res[0].sum!=None:
						# 	d_val.append(res[0].sum)
						# else:
						# 	d_val.append(0)
						if it.fieldname!='Name':
							docs=next((x.fieldtype for x in docfields if x.fieldname==it.fieldname),None)
						else:
							docs='Link'
						if docs=='Int' or docs=='Float' or docs=='Currency':
							d_val.append(sum(res[it.fieldname] for res in result))
						else:
							d_val.append(len(result))
					datasets.append({'values':d_val,'name':it.label,'chartType':it.chart_type.lower()})
					color.append(it.color)
			ids=item.parent+item.name
			chartslist.append({'label':months,'dataset':datasets,'title':chart.display_text,'id':ids,'color':color,'type':chart.graph_type.lower(),'size':item.display_type})
		return chartslist

@frappe.whitelist()
def get_listings(dashboard):
	listing=[]
	lists=frappe.db.get_all('Dashboard List',filters={'parent':dashboard[0].name},fields=['*'])
	today=getdate(nowdate())
	now=datetime.now()
	if lists:
		default_currency=frappe.db.get_single_value('Global Defaults','default_currency')
		currency=frappe.get_value('Currency',default_currency,'symbol')
		for item in lists:
			table=frappe.get_doc('Dashboard Items',item.title)
			ignore_permissions=False if table.check_user_permissions else True
			filters=[]
			if table.conditions:
				for c in table.conditions:
					symbol=c.condition_symbol
					if symbol.find('&lt;')!=-1:
						symbol=symbol.replace('&lt;','<')
					elif symbol.find('&gt;')!=-1:
						symbol=symbol.replace('&gt;','>')				
					fil=[c.fieldname,'{0}'.format(symbol)]
					if c.condition_symbol=='not in' or c.condition_symbol=='in':
						fil.append(c.value.split('\n'))
					else:
						if c.fieldtype=='Date' and c.value=='Today':
							fil.append(today)
						elif c.fieldtype=='Datetime' and c.value=='Today':							
							fil.append(now)
						else:
							fil.append(c.value)
					filters.append(fil)
					
			# fields_list=table.fields_to_specify[:-1].split(',')
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
				# 	ftype=next((x.fieldtype for x in docfields if x.fieldname==fi))
				# new_fld={'id':fi,'resizable':True,'sortable':True,'name':fi.replace('_',' ').capitalize(),'fieldtype':ftype}
				# if ftype=='Link':					
				# 	new_fld['format']='(value)=>{return `<a href="#Form/'+docs+'/${value}">${value}</a>`}'
				# elif ftype=='Currency':
				# 	new_fld['format']='(value)=>{return `'+currency+' ${value}`}'
				# 	new_fld['align']='right'
				new_fld={'id':fi.fieldname,'name':fi.display_name,'resizable':fi.resizable,'sortable':fi.sortable,'focusable':fi.focusable}
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
						new_fld['format']='(value)=>{return `'+currency+' ${value}`}'
						new_fld['align']='right'
					elif ftype=='Float' or ftype=='Int':
						new_fld['align']='right'
				fields.append(fi.fieldname)
				fields_arr.append(new_fld)
			# query=table.query_field
			# if table.no_of_data:
			# 	query=query+' limit {limit}'.format(limit=table.no_of_data)
			# res=frappe.db.sql('''{query}'''.format(query=query))
			res=frappe.get_list(table.reference_doctype,fields=fields,filters=filters,limit_page_length=table.no_of_data,order_by='modified desc',ignore_permissions=ignore_permissions)
			ids=item.parent+item.name
			listing.append({'data':res,'fields':fields_arr,'doctype':table.reference_doctype,'title':table.display_text,'size':item.display_type,'id':ids})
	return listing

@frappe.whitelist()
def get_dashboard_items(name):
	dashboard=frappe.db.get_all('Dashboards',filters={'name':name},fields=['*'])
	lists=[]
	if dashboard:
		dashboard_items=frappe.db.get_all('Dashboard Counters List',fields=['type','items','column_width','no_of_counters'],
		filters={'parent':dashboard[0].name},order_by='idx')
		if dashboard_items:
			for item in dashboard_items:
				if item.type=='Counter':
					counters_list=frappe.db.get_all('Dashboard Items',filters={'type':'Counter','group':item.items},fields=['*'])
					counter_data=get_counters_new(counters_list)
					if counter_data:
						item.counter_list=counter_data
				else:
					graph=frappe.db.get_all('Dashboard Items',filters={'type':item.type,'name':item.items},fields=['*'])
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
					symbol=c.condition_symbol
					if symbol.find('&lt;')!=-1:
						symbol=symbol.replace('&lt;','<')
					elif symbol.find('&gt;')!=-1:
						symbol=symbol.replace('&gt;','>')
					fil=[c.fieldname,symbol]
					if c.condition_symbol=='not in' or c.condition_symbol=='in':
						fil.append(c.value.split('\n'))
					else:
						if c.fieldtype=='Date' and c.value=='Today':
							fil.append(today)
						elif c.fieldtype=='Datetime' and c.value=='Today':
							now=datetime.now()
							fil.append(now)
						else:
							fil.append(c.value)
					filters.append(fil)
			if dash.date_range=='Daily':
				fil1=["creation","=",today]
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
				counter.append({'title':dash.display_text,'count':len(result),'css':dash.css_style})
			else:
				total=sum(res[dash.referred_field] for res in result)
				counter.append({'title':dash.display_text,'count':("%0.2f" % total),'css':dash.css_style})
	return counter

@frappe.whitelist()
def get_graph_new(graph_list):
	months=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
	today=getdate(nowdate())
	chartslist=[]	
	if graph_list:
		for item in graph_list:
			chart=frappe.get_doc('Dashboard Items',item.name)
			res=frappe.db.sql('''select count(*) as count from `tab{doctype}`'''.format(doctype=chart.reference_doctype),as_dict=1)		
			color=[]
			datasets=[]			
			docfields=frappe.get_meta(chart.reference_doctype).get("fields")
			if chart.datasets:
				for it in chart.datasets:
					d_val=[]
					month=0
					while month<12:
						month=month+1
						st_date=datetime(year=today.year,day=01,month=month)
						next_month = st_date.replace(day=28) + timedelta(days=4)
						ed_date=next_month - timedelta(days=next_month.day)
						ignore_permissions=False if chart.check_user_permissions else True
						filters_g=[]
						if chart.conditions:
							for c in chart.conditions:
								if c.condition_for==it.name:
									symbol=c.condition_symbol
									if symbol.find('&lt;')!=-1:
										symbol=symbol.replace('&lt;','<')
									elif symbol.find('&gt;')!=-1:
										symbol=symbol.replace('&gt;','>')
									fil=[c.fieldname,symbol]
									if c.condition_symbol=='not in' or c.condition_symbol=='in':
										fil.append(c.value.split('\n'))
									else:
										if c.fieldtype=='Date' and c.value=='Today':
											fil.append(today)
										elif c.fieldtype=='Datetime' and c.value=='Today':
											now=datetime.now()
											fil.append(now)
										else:
											fil.append(c.value)
									filters_g.append(fil)
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
					datasets.append({'values':d_val,'name':it.label,'chartType':it.chart_type.lower()})
					color.append(it.color)
			ids=item.name.replace(' ','').lower()
			chartslist.append({'label':months,'dataset':datasets,'title':chart.display_text,'id':ids,'color':color,'type':chart.graph_type.lower(),'size':item.display_type})
		return chartslist

@frappe.whitelist()
def get_table_new(table_list):
	listing=[]
	today=getdate(nowdate())
	now=datetime.now()
	if table_list:
		default_currency=frappe.db.get_single_value('Global Defaults','default_currency')
		currency=frappe.get_value('Currency',default_currency,'symbol')
		for item in table_list:
			table=frappe.get_doc('Dashboard Items',item.name)
			ignore_permissions=False if table.check_user_permissions else True
			filters=[]
			if table.conditions:
				for c in table.conditions:
					symbol=c.condition_symbol
					if symbol.find('&lt;')!=-1:
						symbol=symbol.replace('&lt;','<')
					elif symbol.find('&gt;')!=-1:
						symbol=symbol.replace('&gt;','>')				
					fil=[c.fieldname,'{0}'.format(symbol)]
					if c.condition_symbol=='not in' or c.condition_symbol=='in':
						fil.append(c.value.split('\n'))
					else:
						if c.fieldtype=='Date' and c.value=='Today':
							fil.append(today)
						elif c.fieldtype=='Datetime' and c.value=='Today':							
							fil.append(now)
						else:
							fil.append(c.value)
					filters.append(fil)					
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
				new_fld={'id':fi.fieldname,'name':fi.display_name,'resizable':fi.resizable,'sortable':fi.sortable,'focusable':fi.focusable}
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
						new_fld['format']='(value)=>{return `'+currency+' ${value}`}'
						new_fld['align']='right'
					elif ftype=='Float' or ftype=='Int':
						new_fld['align']='right'
				fields.append(fi.fieldname)
				fields_arr.append(new_fld)
			res=frappe.get_list(table.reference_doctype,fields=fields,filters=filters,limit_page_length=table.no_of_data,order_by='modified desc',ignore_permissions=ignore_permissions)
			ids=item.name.replace(' ','').lower()
			listing.append({'data':res,'fields':fields_arr,'doctype':table.reference_doctype,'title':table.display_text,'size':item.display_type,'id':ids})
	return listing