# -*- coding: utf-8 -*-
# Copyright (c) 2021, DAS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import requests
import json
import base64

class TokopediaSetting(Document):
	def validate(self):
		sample_string = self.client_id+":"+self.clien_secret
		test = str(sample_string)
		encodedBytes = base64.b64encode(test.encode("utf-8"))
		encodedStr = str(encodedBytes, "utf-8")
		self.basic_base_64 = encodedStr

		url_t = "https://accounts.tokopedia.com/token?grant_type=client_credentials"
		payload_t ={}
		headers_t = {
			'Authorization': 'Basic '+self.basic_base_64,
	  	  	'Content-Length': '0',
	    	'User-Agent': 'PostmanRuntime/7.17.1'
		}
		response_t = requests.request("POST", url_t, headers=headers_t, data=payload_t)
		tokens = json.loads(response_t.text)
		self.token = tokens['access_token']
		
		url = "https://fs.tokopedia.net/v1/shop/fs/"+self.app_id+"/shop-info"
		payload={}
		headers = {
			'Authorization': 'Bearer '+self.token
		}
		response = requests.request("GET", url, headers=headers, data=payload)
		datatest = json.loads(response.text)
		self.shop_id = datatest['data'][0]['shop_id']
		self.shop_name = datatest['data'][0]['shop_name']
		self.shop_url = datatest['data'][0]['shop_url']
		# for i in datatest['data']:
		# 	get_shop = frappe.get_value("List Shop",{"shop_id" : i['shop_id']}, "shop_id")
		# 	if get_shop:
		# 		frappe.msgprint("Shop Id "+ get_shop+ " Sudah Ada")
		# 	else :
		# 		row = self.append('list_shop', {})
		# 		row.shop_id = i['shop_id']
		# 		row.shop_name = i['shop_name']
		# 		row.url = i['shop_url']