# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt
from __future__ import unicode_literals

import json
import frappe
import frappe.handler
import frappe.client
from frappe.utils.response import build_response
from frappe import _
from six.moves.urllib.parse import urlparse, urlencode

@frappe.whitelist()
def get_dashboard_items_for_menu():
	# dashboard=frappe.db.get_all('Dashboards',fields=['module','title'],order_by='module')
	# return dashboard
	dashboard=frappe.db.sql('''select d.name,d.module,d.title from `tabDashboards` d left join 
		`tabDashboard Roles` dr on dr.parent=d.name left join `tabHas Role` hr on hr.role=dr.role 
		left join `tabUser` u on u.name=hr.parent where u.name=%(user)s group by d.name 
		order by d.module,d.creation asc''',{'user':frappe.session.user},as_dict=1)
	return dashboard