from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Lazada Connector"),
			"items": [
				{
					"type": "doctype",
					"name": "Lazada Store",
					"description":_("Lazada Store"),
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "Lazada Order",
					"description":_("Lazada Order"),
					"onboard": 1,
				},
				
			]
		},

	]