# -*- coding: utf-8 -*-
# Copyright (c) 2018, info@valiantsystems.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe.model.document import Document
from frappe.share import add
from frappe import _, throw
from frappe.utils import getdate, add_months, get_last_day, nowdate
from frappe.utils import flt
from datetime import datetime, timedelta

class DashboardDetailView(Document):
	pass

@frappe.whitelist()
def get_dashboard_doc_counter(doctype_name,docname):
	if doctype_name:
		
		dashboard=frappe.db.get_all('Dashboard Detail View',filters={'doctype_name':doctype_name},fields=['*'])
		if dashboard:
			counterlist=get_doc_counters(dashboard,docname)
			return counterlist
	

@frappe.whitelist()
def get_doc_counters(dashboard,docname):
	counter=[]
	counters=frappe.db.get_all('Detail Counters',filters={'parent':dashboard[0].name},fields=['*'],order_by='idx')
	if counters:
		today=getdate(nowdate())
		for item in counters:
			dash=frappe.get_doc('Dashboard Items',item.title)
			ignore_permissions=False if dash.check_user_permissions else True
			filters=[]
			
			res=frappe.db.sql('''select count(*) as count from `tab{doctype}`'''.format(doctype=dash.doctype),as_dict=1)
			
			if docname and dash.referred_parent_field:
				fils=[dash.referred_parent_field,"=",docname]
				filters.append(fils)

			if dash.conditions:
				for c in dash.conditions:
					fil=[c.fieldname,c.condition_symbol,c.value]
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
			
			if dash.is_child_table_based!=1:
				result=frappe.get_list(dash.reference_doctype,fields=['*'],filters=filters,ignore_permissions=ignore_permissions,limit_page_length=res[0].count)
	
			elif dash.is_child_table_based==1:
				print dash.query_field
				result=frappe.db.sql("""{query}""".format(query=dash.query_field),as_dict=1)
				
			if dash.counter_type=='Count' and dash.is_child_table_based!=1:
				counter.append({'title':dash.display_text,'count':len(result),'size':dashboard[0].counter_count,'css':dash.css_style})
			elif dash.counter_type=='Sum' and dash.is_child_table_based!=1:
				
				
				counter.append({'title':dash.display_text,'count':sum(sums[dash.referred_field] for sums in result),'size':dashboard[0].counter_count,'css':dash.css_style})					
			if dash.counter_type=='Count' and dash.is_child_table_based==1:
				counter.append({'title':dash.display_text,'count':result[0].sum,'size':dashboard[0].counter_count,'css':dash.css_style})
			
			elif dash.counter_type=='Sum' and dash.is_child_table_based==1:
				
				counter.append({'title':dash.display_text,'count':result[0].sum,'size':dashboard[0].counter_count,'css':dash.css_style})					
		
	return counter

@frappe.whitelist()
def get_fields_label(doctype):
	fields=[
		{
			"fieldname":"name",
			"label":"Name",
			"fieldtype":"Link",
			"hidden":"0"
		},
		{
			"fieldname":"creation",
			"label":"Created On",
			"fieldtype":"Datetime",
			"hidden":"0"
		},
		{
			"fieldname":"modified",
			"label":"Modified On",
			"fieldtype":"Datetime",
			"hidden":"0"
		},
		{
			"fieldname":"owner",
			"label":"Created By",
			"fieldtype":"Link",
			"hidden":"0"
		},
		{
			"fieldname":"modified_by",
			"label":"Modified By",
			"fieldtype":"Link",
			"hidden":"0"
		},
		{
			"fieldname":"docstatus",
			"label":"Document Status",
			"fieldtype":"Int",
			"hidden":"0"
		}
	]
	fields+=[{"fieldname": df.fieldname or "", "label": _(df.label or ""), "fieldtype": _(df.fieldtype or ""), "hidden": _(df.hidden)}
		for df in frappe.get_meta(doctype).get("fields")]
	return fields

@frappe.whitelist()
def get_fields_labels_list(doctype=None):
	return [{"fieldname": df.fieldname or "", "label": _(df.label or ""), "fieldtype": _(df.fieldtype or ""), "hidden": _(df.hidden)}
		for df in frappe.get_meta(doctype).get("fields")]


@frappe.whitelist()
def get_fields_label_with_options(doctype=None):
	return [{"fieldname": df.fieldname or "", "label": _(df.label or ""), "fieldtype": _(df.fieldtype or ""), "hidden": _(df.hidden),"options": _(df.options)}
		for df in frappe.get_meta(doctype).get("fields")]