from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Orders"),
			"items": [
				{
					"type": "doctype",
					"name": "Marketplace Order",
					"description":_("Marketplace Order"),
					"onboard": 1,
				},
				
				
			]
		},
		{
			"label": _("Shopee"),
			"items": [
				
				{
					"type": "doctype",
					"name": "Shopee Store Setting",
					"description":_("Shopee Store Setting"),
					"onboard": 1,
				},
				
			]
		},
		{
			"label": _("Tokopedia"),
			"items": [
				
				{
					"type": "doctype",
					"name": "Tokopedia Store Setting",
					"description":_("Tokopedia Store Setting"),
					"onboard": 1,
				},
				
			]
		},
		{
			"label": _("Lazada"),
			"items": [
				
				{
					"type": "doctype",
					"name": "Lazada Store Setting",
					"description":_("Lazada Store Setting"),
					"onboard": 1,
				},
				
			]
		},

		
	]