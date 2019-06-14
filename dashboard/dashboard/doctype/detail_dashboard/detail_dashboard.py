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

class DetailDashboard(Document):
	def on_update(self):
		
		if self.doctype_name:
			lists=frappe.db.get_all('Detail Dashboard',filters={'doctype_name':['in',self.doctype_name]})
			if not lists:
				frappe.throw(frappe._('Dashboard for this doctype have already been created. Please select any other doctype.'))


