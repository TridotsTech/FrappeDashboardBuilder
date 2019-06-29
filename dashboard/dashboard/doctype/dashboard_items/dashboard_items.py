# -*- coding: utf-8 -*-
# Copyright (c) 2018, info@valiantsystems.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class DashboardItems(Document):
	def autoname(self):
		self.name=self.display_text+' - '+self.type

	def validate(self):		
		if self.type=='Counter':
			self.query_field=set_counter_query(self)
			self.css_style=set_css_property(self)
		elif self.type=='Table':
			self.query_field=set_table_query(self)
		else:
			assign_condition_query(self)

@frappe.whitelist()
def set_counter_query(self):
	query=''
	if self.counter_type=='Count':
		query='SELECT count(doc.*) as count from `tab{doctype}` doc'.format(doctype=self.reference_doctype)
	else:
		query='SELECT sum(doc.{field}) as sum from `tab{doctype}` doc'.format(doctype=self.reference_doctype,field=self.referred_field)
	if self.is_child_table_based==1 and self.reference_child_doc_name:
		query+=',`tab{childdoc}` childdoc'.format(childdoc=self.reference_child_doc_name)
	if self.date_range=='Daily':
		query+=' where CAST(creation as DATE)=CURDATE()'
	elif self.date_range=='Weekly':
		query+=' where creation BETWEEN CURDATE() and DATE_SUB(CURDATE(), INTERVAL 7 DAY)'
	elif self.date_range=='Monthly':
		query+=' where MONTH(CURDATE())=MONTH(creation)'
	if self.date_range!="All Time":
		query+=', childdoc.name=doc.name'
	elif self.is_child_table_based==1 and self.date_range=="All Time":
		query+=' where childdoc.parent=doc.name'
	
	docfields=frappe.get_meta(self.reference_doctype).get("fields")
	if self.conditions:
		for cond in self.conditions:
			if not cond.fieldtype:
				cond.fieldtype=next((x.fieldtype for x in docfields if x.fieldname==cond.fieldname),None)
			if query.find('where')==-1:
				query+=' where '
			else:
				query+=' and '
			conditions=get_cond_query(cond)
			if conditions:
				query+=conditions	
	return query

def get_cond_query(cond):
	query=''
	if cond.condition=='Equals':
		cond.condition_symbol='='
		query+='doc.{field} = "{value}"'.format(field=cond.fieldname,value=cond.value)
	elif cond.condition=='Not Equals':
		cond.condition_symbol='!='
		query+='doc.{field} != "{value}"'.format(field=cond.fieldname,value=cond.value)
	elif cond.condition=='Like':
		cond.condition_symbol='like'
		query+='doc.{field} like "%{value}%"'.format(field=cond.fieldname,value=cond.value)
	elif cond.condition=='Not Like':
		cond.condition_symbol='not like'
		query+='doc.{field} not like "%{value}%"'.format(field=cond.fieldname,value=cond.value)
	elif cond.condition=='In':
		cond.condition_symbol='in'
		values=cond.value.split('\n')
		val='"'+'","'.join(values)+'"'
		query+='{field} in ({value})'.format(field=cond.fieldname,value=val)
	elif cond.condition=='Not In':
		cond.condition_symbol='not in'
		values=cond.value.split('\n')
		val='"'+'","'.join(values)+'"'
		query+='{field} not in ({value})'.format(field=cond.fieldname,value=val)
	else:
		cond.condition_query=cond.condition
		query+='doc.{field} {operator} "{value}"'.format(field=cond.fieldname,operator=cond.condition,value=cond.value)
	return query

@frappe.whitelist()
def set_table_query(self):
	query='select '
	if self.fields_to_specify:
		query+=self.fields_to_specify[:-1]
	else:
		query+='*'
	query+=' from `tab{doctype}`'.format(doctype=self.reference_doctype)
	query=assign_conditions(self,query)
	return query
	
@frappe.whitelist()
def assign_conditions(self,query):
	if self.conditions:
		docfields=frappe.get_meta(self.reference_doctype).get("fields")
		for cond in self.conditions:
			if not cond.fieldtype:
				cond.fieldtype=next((x.fieldtype for x in docfields if x.fieldname==cond.fieldname),None)
			if query.find('where')==-1:
				query+=' where '
			else:
				query+=' and '
			conditions=get_cond_query(cond)
			if conditions:
				query+=conditions
	return query

@frappe.whitelist()
def assign_condition_query(self):
	query=''
	docfields=frappe.get_meta(self.reference_doctype).get("fields")
	if self.datasets:
		for item in self.datasets:			
			if self.conditions:				
				for c in self.conditions:
					if not c.fieldtype:
						c.fieldtype=next((x.fieldtype for x in docfields if x.fieldname==c.fieldname),None)
					if c.condition_for==item.name:
						query+=' and '
						conditions=get_cond_query(c)
						if conditions:
							query+=conditions
			item.condition_query=query
	else:
		query='select '
		datef=next((x.fieldname for x in docfields if x.label==self.date_fields),None)
		if self.value_type=='Count':
			query+='count(*) as value'
		elif self.value_type=='Sum':
			field=next((x.fieldname for x in docfields if x.label==self.value_fields),None)
			query+='sum({field}) as value'.format(field=field)
		query+=',{field} as label from `tab{doctype}`'.format(doctype=self.reference_doctype,field=datef)
		query=assign_conditions(self,query)		
		query+=' group by {field}'.format(field=datef)
		query+=' order by value {type}'.format(type=('asc' if self.order_by=='Ascending' else 'desc'))
		query+=' limit {limit}'.format(limit=(self.no_of_graph_records if self.no_of_graph_records>0 else 10))
		self.query_field=query


@frappe.whitelist()
def set_css_property(self):
	css=''
	if self.text_color:
		css+='color:'+self.text_color+';'
	if self.bg_type=='Image Background':
		if self.background_image:
			css+='background-image:url("'+self.background_image+'");'
	elif self.bg_type=='Gradient Background':
		if self.gradient_type=='Linear':
			css+='background-image:linear-gradient(to '+self.linear_gradient_direction.lower()+','+self.bg_1+','+self.bg_2+');'
		else:
			css+='background-image:radial-gradient('+self.bg_1+','+self.bg_2+');'
	else:
		css+='background:'+self.bg_1+';'
	return css