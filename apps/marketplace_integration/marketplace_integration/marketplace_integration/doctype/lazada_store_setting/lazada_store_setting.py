# -*- coding: utf-8 -*-
# Copyright (c) 2021, DAS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import time, datetime
from lazada_connector.lazada_connector.doctype.lazada_store.lazop.base import LazopClient, LazopRequest

class LazadaStoreSetting(Document):

	def generate_url_for_authorization_code(self):
		if not self.api_key and not self.redirect_url :
			frappe.throw("You must enter the API Key and Redirect URL")

		self.url_for_authorization_code = str("""https://auth.lazada.com/oauth/authorize?response_type=code&force_auth=true&redirect_uri={0}&client_id={1}""".format(self.redirect_url, self.api_key))


	def validate(self):
		if not self.url_store :
			frappe.throw("Please input URL Store first")

		if not self.api_key and not self.api_secret :
			frappe.throw("Please input API Key and API Secret first")

		if not self.authorization_code :
			frappe.throw("Please input Authorization Code first")


		client =  LazopClient("https://auth.lazada.com/rest", self.api_key ,self.api_secret)
		
		if not self.access_token and not self.refresh_token :
			# generate access token dan refresh token
			request = LazopRequest("/auth/token/create",'GET')
			request.add_api_param('code', self.authorization_code)
			# request.add_api_param('limit', '100')
			response = client.execute(request)
			print(response.type)
			# frappe.throw(str(response.body))

			# {'access_token': '50000900618qgnrLfzFmCnZmrEZZlu11e4e35bEpRd0vCeeCyepuuigIvYYuAKof', 'country': 'id', 'refresh_token': '50001900a18Nk38iBw4rsZCyhYdIva10ff08d8TwEakhPBnT2DkgKmwISkmtGaTr', 'account_platform': 'seller_center', 'refresh_expires_in': 2592000, 'country_user_info': [{'country': 'id', 'user_id': '400612590379', 'seller_id': '400612590379', 'short_code': 'ID67XJTW0U'}], 'expires_in': 604800, 'account': 'dummyriconova@gmail.com', 'code': '0', 'request_id': '0b8b48f316239119420041252'}

			self.access_token = response.body["access_token"]
			self.refresh_token = response.body["refresh_token"]

		# ambil seller info
		client = LazopClient(self.url_store, self.api_key, self.api_secret)
		request1 = LazopRequest('/seller/get','GET')
		response1 = client.execute(request1, self.access_token)
		# frappe.msgprint(str(response1.body))

		if response1 :

			self.shop_name = response1.body["data"]["name"]
			self.location = response1.body["data"]["location"]
			self.seller_id = response1.body["data"]["seller_id"]
			self.seller_email = response1.body["data"]["email"]


@frappe.whitelist()
def create_access_token_daily():

	# ambil data store nya dulu
	get_store = frappe.db.sql("""
		SELECT ss.`name` 
		FROM `tabLazada Store Setting` ss
		WHERE ss.`enable_sync` = 1
		AND ss.`store_location` != ""
		AND ss.`url_store` != ""
		AND ss.`api_key` != ""
		AND ss.`authorization_code` != ""
		AND ss.`access_token` = ""
	""")

	if get_store :
		for gs in get_store :

			store_name = str(gs[0])
			lazada_setting = frappe.get_doc("Lazada Store Setting", store_name)

			client =  LazopClient("https://auth.lazada.com/rest", lazada_setting.api_key ,lazada_setting.api_secret)
			request = LazopRequest("/auth/token/create",'GET')
			request.add_api_param('code', self.authorization_code)
			# request.add_api_param('limit', '100')
			response = client.execute(request)
			print(response.type)
			print(response.body)

			# {'access_token': '50000900618qgnrLfzFmCnZmrEZZlu11e4e35bEpRd0vCeeCyepuuigIvYYuAKof', 'country': 'id', 'refresh_token': '50001900a18Nk38iBw4rsZCyhYdIva10ff08d8TwEakhPBnT2DkgKmwISkmtGaTr', 'account_platform': 'seller_center', 'refresh_expires_in': 2592000, 'country_user_info': [{'country': 'id', 'user_id': '400612590379', 'seller_id': '400612590379', 'short_code': 'ID67XJTW0U'}], 'expires_in': 604800, 'account': 'dummyriconova@gmail.com', 'code': '0', 'request_id': '0b8b48f316239119420041252'}

			lazada_setting.access_token = response.body["access_token"]
			lazada_setting.refresh_token = response.body["refresh_token"]

			lazada_setting.flags.ignore_permissions = True
			lazada_setting.save()