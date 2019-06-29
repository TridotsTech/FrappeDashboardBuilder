from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label":_("Dashboard"),
			"icon":_("fa fa-home"),
			"items":[
				{
					"type": "doctype",
					"name": "Dashboards"
				},
				{
					"type": "doctype",
					"name": "Dashboard Items"
				},
				{
					"type": "doctype",
					"name": "Dashboard Groups"
				}
			]
		}
	]