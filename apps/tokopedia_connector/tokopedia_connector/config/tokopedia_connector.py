from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Tokopedia"),
			"items": [
				{
					"type": "doctype",
					"name": "Tokopedia Orders",
					"description":_("Tokopedia Orders"),
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "Tokopedia Setting",
					"description":_("Tokopedia Setting"),
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "List Promo",
					"description":_("List Promo"),
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "List Shop",
					"description":_("List Shop"),
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "List Category Tokopedia",
					"description":_("List Category"),
					"onboard": 1,
				},
				
			]
		},

		
	]