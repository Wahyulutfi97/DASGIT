# -*- coding: utf-8 -*-
# Copyright (c) 2020, riconova and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import time, datetime
from lazada_connector.lazada_connector.doctype.lazada_store.lazop.base import LazopClient, LazopRequest

class LazadaStore(Document):

	def test_sync(self):
		if not self.url_store :
			frappe.throw("Please input URL Store first")

		if not self.api_key and not self.api_secret :
			frappe.throw("Please input API Key and API Secret first")

		client = LazopClient(self.url_store, self.api_key, self.api_secret)
		# create a api request set GET mehotd
		# default http method is POST
		request = LazopRequest('/seller/get','GET')

		# simple type params ,Number ,String
		# request.add_api_param('api_id','1')

		# response = client.execute(request)
		response = client.execute(request, self.access_token)

		if response :

			self.status_test_sync = str(response.body) + "\n\n" + "Connection Success"
			self.store_name = response.body["data"]["name"]
			self.location = response.body["data"]["location"]
			self.seller_id = response.body["data"]["seller_id"]
			self.seller_email = response.body["data"]["email"]

		else :
			self.status_test_sync = "Connection Failed, Please check again your Data"

		# full response
		# frappe.throw(str(response.body))

	def validate(self):
		if not self.store_name :
			frappe.throw("Please click button Test Sync first")



	def generate_url_for_authorization_code(self):
		if not self.api_key and not self.redirect_url :
			frappe.throw("You must enter the API Key and Redirect URL")

		self.url_for_authorization_code = str("""https://auth.lazada.com/oauth/authorize?response_type=code&force_auth=true&redirect_uri={0}&client_id={1}""".format(self.redirect_url, self.api_key))



@frappe.whitelist()
def get_timestamp():
	client =  LazopClient("https://api.lazada.co.id/rest", "123109" ,"zsgL5cRJyn01VG6VVJq2OlLV2JsEjgCl")
	request = LazopRequest('/brands/get','GET')
	request.add_api_param('offset', '0')
	request.add_api_param('limit', '100')
	response = client.execute(request)
	print(response.type)
	print(response.body)




@frappe.whitelist()
def create_access_token_daily():

	# ambil data store nya dulu
	get_store = frappe.db.sql("""
		SELECT ss.`name` 
		FROM `tabLazada Store` ss
		WHERE ss.`disable` = 0
		AND ss.`store_location` != ""
		AND ss.`url_store` != ""
		AND ss.`api_key` != ""
		AND ss.`authorization_code` != ""
		AND ss.`access_token` = ""
	""")

	if get_store :
		for gs in get_store :

			store_name = str(gs[0])
			lazada_setting = frappe.get_doc("Lazada Store", store_name)

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

@frappe.whitelist()
def refresh_access_token_daily():

	# ambil data store nya dulu
	get_store = frappe.db.sql("""
		SELECT ss.`name` 
		FROM `tabLazada Store` ss
		WHERE ss.`disable` = 0
		AND ss.`store_location` != ""
		AND ss.`url_store` != ""
		AND ss.`api_key` != ""
		AND ss.`authorization_code` != ""
		AND ss.`access_token` != ""
	""")

	if get_store :
		for gs in get_store :

			store_name = str(gs[0])
			lazada_setting = frappe.get_doc("Lazada Store", store_name)

			client =  LazopClient("https://auth.lazada.com/rest", lazada_setting.api_key ,lazada_setting.api_secret)
			request = LazopRequest("/auth/token/create",'GET')
			request.add_api_param('code', self.authorization_code)
			# request.add_api_param('limit', '100')
			response = client.execute(request)
			print(response.type)
			print(response.body)