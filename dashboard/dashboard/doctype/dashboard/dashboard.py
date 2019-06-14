# -*- coding: utf-8 -*-
# Copyright (c) 2018, info@valiantsystems.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Dashboard(Document):
	pass


@frappe.whitelist()
def get_doc_fields(doctype):
	fields=frappe.db.sql('''select fieldname from `tabDocField` where parent=%(name)s''',{'name':doctype})
	return fields