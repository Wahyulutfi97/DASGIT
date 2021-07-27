# -*- coding: utf-8 -*-
# Copyright (c) 2021, PT DAS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

from marketplace_connector.marketplace_connector.doctype.frappeclient import FrappeClient
from marketplace_connector.marketplace_connector.doctype.shopee_shop_setting.shopee_connector.client import Client
from marketplace_connector.marketplace_connector.doctype.shopee_shop_setting.shopee_connector.shopcategory import ShopCategory

import json
import os
import requests
import subprocess
from frappe.utils.background_jobs import enqueue
from frappe.utils import get_site_name

from frappe import utils
from frappe.utils import nowdate, add_days, random_string, get_url

import time
import datetime
from numpy import asarray

from frappe import utils

import hmac
import time
import hashlib
import requests

class ShopeeShopSetting(Document):

	def generate_url_for_shop_id(self):
		if not self.partner_id :
			frappe.throw("Partner ID harus diisi")

		if not self.partner_key :
			frappe.throw("Partner Key harus diisi")

		if not self.redirect_url :
			frappe.throw("Redirect URL harus diisi")

		# # def api1 generator url
		timest = int(time.time())
		path = "/api/v1/shop/auth_partner"
		host = "https://partner.shopeemobile.com"
		partner_id = self.partner_id
		# partner_id = 3863
		redirect= self.redirect_url
		partner_key = self.partner_key
		token = partner_key+redirect
		hash_token = hashlib.sha256(token.encode()).hexdigest()
		url = host+path+"?id={}&redirect={}&token={}".format(partner_id,redirect,hash_token)

		# test_host = "https://partner.uat.shopeemobile.com/api/v1/shop/auth_partner"
		# test_id = 100958
		# test_key = "27fc6a405e1443e4853f9915ef65babb3c60b0dec6cab25450757405e1abb1bf"
		# test_token = hashlib.sha256((test_key+redirect).encode("utf-8")).hexdigest()
		# url = test_host+"?id={}&token={}&redirect={}".format(test_id,test_token,redirect)
		self.url_shop_id = url
		# resp = requests.get(url)
		# print(resp.content)

	@frappe.whitelist()
	def test_button():
		msgprint("call me")

	@frappe.whitelist()
	def addProduct(self, product_name, category_id, description, price, stock, images, weight, attributes, logistic): 
		if self.enable_sync :
			if self.shop_id and self.partner_id and self.partner_key :
				shopid = int(self.shop_id)
				partnerid = int(self.partner_id)
				api_key = str(self.partner_key)
				shopeeclient = Client(shopid, partnerid, api_key)
				product_data = {
					"name": product_name,
					"category_id": category_id,
					"description": description,
					"price": price,
					"stock": stock,
					"images": images,
					"weight": weight,
					'attributes': attributes,
					'logistics': logistic
            	}
				shopeeAddProduct = shopeeclient.product.add(product_data)
				return shopeeAddProduct

	def validate(self):
		if self.enable_sync :
			if self.shop_id and self.partner_id and self.partner_key :
				shopid = int(self.shop_id)
				partnerid = int(self.partner_id)
				api_key = str(self.partner_key)
				shopeeclient = Client(shopid, partnerid, api_key)

				shopeeCategory = shopeeclient.item.get_categories()
				category_id = shopeeCategory['categories'][0]
				category = {
					"category_id": int(category_id['category_id'])
				}
				shopeeAttributes = shopeeclient.item.get_attributes(category)

				# product_data = {
				# 	"name": product_name,
				# 	"category_id": category_id,
				# 	"description": description,
				# 	"price": price,
				# 	"stock": stock,
				# 	"images": [{"url":"https://www.wallpapertip.com/wmimgs/207-2078090_gambar-gambar-untuk-wallpaper.jpg"}],
				# 	"weight": 1,
				# 	'attributes': [{'attributes_id': 21460, 'attribute_name': 'Merek', 'is_mandatory': True, 'attribute_type': 'STRING_TYPE', 'format_type': 'NORMAL', 'input_type': 'COMBO_BOX', 'value': 'Tidak Ada Merek'}],
				# 	'logistics': [{'weight_limits': {'item_min_weight': 0, 'item_max_weight': 100.0}, 'mask_channel_id': 0, 'item_max_dimension': {'width': 0, 'length': 0, 'unit': '', 'height': 0}, 'logistic_name': 'Reguler (Cashless)', 'volume_limits': {'item_max_volume': 600000.0, 'item_min_volume': 0}, 'preferred': False, 'has_cod': True, 'sizes': [], 'force_enabled': False, 'enabled': True, 'fee_type': 'SIZE_INPUT', 'logistics_description': 'Layanan pengiriman dengan durasi pengiriman 2-7 hari tergantung lokasi tujuan.', 'logistic_id': 8003}] 
            	# }

				shopeeGetItemList = shopeeclient.product.get_item_list()

				shopeeGetItemDetail = shopeeclient.product.get_item_detail()

				dataCategory = shopeeCategory['categories']
				dataNoChildren = []
				for data in range(len(dataCategory)):
					if dataCategory[data]['has_children'] == False:
						dataNoChildren.append(str(dataCategory[data]))
				# for data in range(len(dataNoChildren)):
				# 	doc = frappe.new_doc("Category Shopee")
				# 	doc.name1 = dataCategory[data]['category_name']
				# 	doc.category_id = dataCategory[data]['category_id']
				# 	doc.save(ignore_permissions = True)

				# for data in range(len(dataNoChildren)):
					# category = {
					# 	"category_id": dataNoChildren[data]['category_id']
					# }
					# shopeeAttributes = shopeeclient.item.get_attributes(category)
				# 	dataShopeeAttributes = shopeeAttributes['attributes'][0]['options']
				# 	for data2 in range(len(dataShopeeAttributes)):
				# 		doc = frappe.new_doc("Brand")
				# 		doc.brand = dataShopeeAttributes[data2]
				# 		doc.brand_id = shopeeAttributes['attributes']
				# 		doc.save(ignore_permissions = True)

				# dataLogistics = shopeeLogistics['logistics'] <--- add logistic to doctype shopee logistic
				# for data in range(len(dataLogistics)):[0]
				# 	doc = frappe.new_doc("Logistic Shopee")
				# 	doc.name1 = dataLogistics[data]['logistic_name']
				# 	doc.logistic_id = dataLogistics[data]['logistic_id']
				# 	doc.description = dataLogistics[data]['logistics_description']
				# 	doc.save(ignore_permissions = True)

				result = shopeeclient.shop.get_shop_info()
				if result :
					frappe.msgprint(str(category_id))
					frappe.msgprint(str(shopeeAttributes['attributes'][0]['attribute_id']))
					frappe.msgprint(str(shopeeAttributes['attributes'][0]))
					# dataShopeeAttributes = shopeeAttributes['attributes'][0]['options']
					# for data2 in range(len(dataShopeeAttributes)):
					# 	doc = frappe.new_doc("Brand")
					# 	doc.brand = dataShopeeAttributes[data2]
					# 	doc.brand_id = shopeeAttributes['attributes'][0]['attribute_id']
					# 	doc.category_id = category_id['category_id']
					# 	doc.save(ignore_permissions = True)
					# frappe.msgprint(str(shopeeLogistics['logistics']))
					# frappe.msgprint(str(shopeeAttributes['attributes'][0]['options']))
					# for i in shopeeCategory.categories:
					# 	if shopeeCategory['categories'][1]['category_name'] == 'Hobi & Koleksi':
					# 		frappe.throw(str(shopeeCategory['categories'])
					self.shop_name = result["shop_name"]
					self.shop_region = result["country"]
					self.shop_status = result["status"]







