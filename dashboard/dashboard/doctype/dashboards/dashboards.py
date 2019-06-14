# -*- coding: utf-8 -*-
# Copyright (c) 2018, info@valiantsystems.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Dashboards(Document):
	def validate(self):
		pass
		# if not self.refer_module:
		# 	lists=frappe.db.get_all('Dashboards',filters={'refer_module':0,'name':['not in',self.name]})
		# 	if lists:
		# 		frappe.throw(frappe._('Dashboard for all modules have already been created. Please select any one module.'))

@frappe.whitelist()
def get_doc_fields(doctype):
	labels=['Section Break','Column Break']
	fields=frappe.db.sql('''select * from `tabDocField` where parent=%(name)s and label not in %(label)s order by idx''',{'name':doctype,'label':labels},as_dict=1)
	return fields

@frappe.whitelist()
def get_doctypes(doctype, txt, searchfield, start, page_len, filters):
	if filters.get('module'):
		return frappe.db.sql('''select name from `tabDocType` where module=%(module)s''',{'module':filters.get('module')})
	else:
		return frappe.db.sql('''select name from `tabDocType`''')

# @frappe.whitelist()
# def frame_counter_query(doctype,counter_type,date_range,check_permissions=False,referred_fied=None):
# 	if counter_type=='Sum':
# 		query='select sum({referred_fied}) from `tab{doctype}`'

@frappe.whitelist()
def get_preview_data(query):
	query="""{query}""".format(query=query)
	return frappe.db.sql(query)

@frappe.whitelist()
def get_graph_query(query):
	# print(query)
	pass