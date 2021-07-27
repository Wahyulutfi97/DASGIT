# -*- coding: utf-8 -*-
# Copyright (c) 2015, erpx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

from lazada_connector.lazada_connector.doctype.lazada_store.lazop.base import LazopClient, LazopRequest

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

from frappe import utils


class SyncMethod(Document):
	pass



# client = lazop.LazopClient(url, appkey ,appSecret)
# request = lazop.LazopRequest('/orders/get','GET')
# request.add_api_param('created_before', '2018-02-10T16:00:00+08:00')
# request.add_api_param('created_after', '2017-02-10T09:00:00+08:00')
# request.add_api_param('status', 'shipped')
# request.add_api_param('update_before', '2018-02-10T16:00:00+08:00')
# request.add_api_param('sort_direction', 'DESC')
# request.add_api_param('offset', '0')
# request.add_api_param('limit', '10')
# request.add_api_param('update_after', '2017-02-10T09:00:00+08:00')
# request.add_api_param('sort_by', 'updated_at')
# response = client.execute(request, access_token)
# print(response.type)
# print(response.body)

# unpaid, pending, canceled, ready_to_ship, delivered, returned, shipped and failed

# client = lazop.LazopClient(url, appkey ,appSecret)
# request = lazop.LazopRequest('/order/items/get','GET')
# request.add_api_param('order_id', '31202')
# response = client.execute(request, access_token)
# print(response.type)
# print(response.body)

@frappe.whitelist()
def calculate_order_status(doc, method):
	
	total_pending = 0
	total_unpaid = 0
	total_ready_to_ship = 0
	total_shipped = 0
	total_delivered = 0
	total_returned = 0
	total_failed = 0
	total_canceled = 0

	if doc.lazada_order_list :
		for i in doc.lazada_order_list :
			# UNPAID/READY_TO_SHIP/SHIPPED/COMPLETED/CANCELLED
			if i.order_status == "pending" :
				total_pending += 1
			elif i.order_status == "unpaid" :
				total_unpaid += 1
			elif i.order_status == "ready_to_ship" :
				total_ready_to_ship += 1
			elif i.order_status == "shipped" :
				total_shipped += 1
			elif i.order_status == "delivered" :
				total_delivered += 1
			elif i.order_status == "returned" :
				total_returned += 1
			elif i.order_status == "failed" :
				total_failed += 1
			elif i.order_status == "canceled" :
				total_canceled += 1


	doc.pending = total_pending
	doc.unpaid = total_unpaid
	doc.ready_to_ship = total_ready_to_ship
	doc.shipped = total_shipped
	doc.delivered = total_delivered
	doc.returned = total_returned
	doc.failed = total_failed
	doc.canceled = total_canceled



@frappe.whitelist()
def get_order_list_lazada():

	# pertama ambil dulu store nya

	get_store = frappe.db.sql("""
		SELECT ss.`name` 
		FROM `tabLazada Store` ss
		WHERE ss.`disable` = 0
		AND ss.`api_key` != ""
		AND ss.`api_secret` != ""
		AND ss.`access_token` != ""
	""")

	if get_store :
		for gs in get_store :

			count = 0

			# create timestamp
			# today_morning = today + " 00:00:00"
			# today_evening = today + " 23:59:59"

			time_from = ""
			time_to = ""

			today = str(utils.today())
			day_sebelumnya = str(add_days(utils.today(), -1));
			today_morning = today + "T00:00:00"
			today_evening = today + "T23:59:59"

			time_from = str(today_morning)
			time_to = str(today_evening)

			# time_from = int(time.mktime(datetime.datetime.strptime(str(today_morning), "%Y-%m-%d %H:%M:%S").timetuple()))
			# time_to = int(time.mktime(datetime.datetime.strptime(str(today_evening), "%Y-%m-%d %H:%M:%S").timetuple()))

			store_name = str(gs[0])

			lazada_setting = frappe.get_doc("Lazada Store", store_name)
			# shopee order name
			temp_name = "LAZADA|"+str(today)+"|"+str(gs[0])

			cari_data = frappe.get_value("Lazada Order", str(temp_name), "name")

			if cari_data : 

				docu = frappe.get_doc("Lazada Order", str(temp_name))

				if lazada_setting.disable == 0 :

					# get credential
					url = lazada_setting.url_store
					appkey = lazada_setting.api_key
					appSecret = lazada_setting.api_secret
					access_token = lazada_setting.access_token

					client = LazopClient(url, appkey ,appSecret)
					request = LazopRequest('/orders/get','GET')

					request.add_api_param('created_before', time_to)
					request.add_api_param('created_after', time_from)
					request.add_api_param('offset', '0')
					request.add_api_param('limit', '10')
					
					response = client.execute(request, access_token)
					print(response.type)
					print(response.body)

					if response.body :

						docu.lazada_order_list = []

						for i in response.body["data"]["orders"] :

							soi = docu.append('lazada_order_list', {})
							soi.order_id = i["order_number"]
							soi.order_status = i["statuses"][0]

							if i["customer_last_name"] :
								soi.customer = i["customer_first_name"] + " " + i["customer_last_name"]
							else :
								soi.customer = i["customer_first_name"]

							# billing
							soi.first_name_billing = i["address_billing"]["first_name"]
							soi.last_name_billing = i["address_billing"]["last_name"]
							soi.address1_billing = i["address_billing"]["address1"]
							soi.address2_billing = i["address_billing"]["address2"]
							soi.address3_billing = i["address_billing"]["address3"]
							soi.address4_billing = i["address_billing"]["address4"]
							soi.address5_billing = i["address_billing"]["address5"]
							soi.city_billing = i["address_billing"]["city"]
							soi.country_billing = i["address_billing"]["country"]
							soi.post_code_billing = i["address_billing"]["post_code"]
							soi.phone_billing = i["address_billing"]["phone"]
							soi.phone2_billing = i["address_billing"]["phone2"]

							# shipping
							soi.first_name_shipping = i["address_shipping"]["first_name"]
							soi.last_name_shipping = i["address_shipping"]["last_name"]
							soi.address1_shipping = i["address_shipping"]["address1"]
							soi.address2_shipping = i["address_shipping"]["address2"]
							soi.address3_shipping = i["address_shipping"]["address3"]
							soi.address4_shipping = i["address_shipping"]["address4"]
							soi.address5_shipping = i["address_shipping"]["address5"]
							soi.city_shipping = i["address_shipping"]["city"]
							soi.country_shipping = i["address_shipping"]["country"]
							soi.post_code_shipping = i["address_shipping"]["post_code"]
							soi.phone_shipping = i["address_shipping"]["phone"]
							soi.phone2_shipping = i["address_shipping"]["phone2"]

							soi.total_amount = i["price"]
							soi.note = i["remarks"]

							soi.shipping_carrier = ""
							soi.tracking_no = ""
							soi.days_to_ship = i["promised_shipping_times"]

							child_client = LazopClient(url, appkey ,appSecret)
							child_request = LazopRequest('/order/items/get','GET')
							child_request.add_api_param('order_id', str(i["order_number"]))
							child_response = client.execute(child_request, access_token)
							
							print(child_response.type)
							print(child_response.body)


							if child_response.body["data"] :
								soi.item_detail = ""
								array_item = []
								temp_array_item = {}
								for a in child_response.body["data"] :

									# frappe.throw( a["recipient_address"]["name"])
									soi.currency = a["currency"]


									temp_array_item = {
										"item_sku" : a["sku"],
										"item_shop_sku" : a["shop_sku"],
										"item_name" : a["name"],
										"item_status" : a["status"],
										"item_item_price" : a["item_price"],
										"item_paid_price" : a["paid_price"],
										"item_warehouse_code" : a["warehouse_code"],
										"item_shipping_type" : a["shipping_type"],
										"item_shipping_provider_type" : a["shipping_provider_type"],
										"item_shipping_fee_original" : a["shipping_fee_original"],
										"item_is_digital" : a["is_digital"],
										
										"item_shipping_service_cost" : a["shipping_service_cost"],
										"item_tracking_code" : a["tracking_code"],
										"item_shipping_amount" : a["shipping_amount"],
										"item_reason_detail" : a["reason_detail"],
										"item_return_status" : a["return_status"],
										"item_shipment_provider" : a["shipment_provider"],
										"item_voucher_amount" : a["voucher_amount"],
										"item_digital_delivery_info" : a["digital_delivery_info"]
									}

									array_item.append(temp_array_item)
								soi.item_detail = str(array_item)

				docu.flags.ignore_permission = True
				docu.save()

			else :
				docu = frappe.new_doc("Lazada Order")
				docu.store = store_name
				docu.date = str(today)
				docu.general_information = """ 
					Date From {} s/d {}
					
				""".format(today_morning, today_evening)

				if lazada_setting.disable == 0 :

					# get credential
					url = lazada_setting.url_store
					appkey = lazada_setting.api_key
					appSecret = lazada_setting.api_secret
					access_token = lazada_setting.access_token

					client = LazopClient(url, appkey ,appSecret)
					request = LazopRequest('/orders/get','GET')

					request.add_api_param('created_before', time_to)
					request.add_api_param('created_after', time_from)
					request.add_api_param('offset', '0')
					request.add_api_param('limit', '10')
					
					response = client.execute(request, access_token)
					print(response.type)
					print(response.body)

					if response.body :

						docu.lazada_order_list = []

						for i in response.body["data"]["orders"] :

							soi = docu.append('lazada_order_list', {})
							soi.order_id = i["order_number"]
							soi.order_status = i["statuses"][0]

							if i["customer_last_name"] :
								soi.customer = i["customer_first_name"] + " " + i["customer_last_name"]
							else :
								soi.customer = i["customer_first_name"]

							# billing
							soi.first_name_billing = i["address_billing"]["first_name"]
							soi.last_name_billing = i["address_billing"]["last_name"]
							soi.address1_billing = i["address_billing"]["address1"]
							soi.address2_billing = i["address_billing"]["address2"]
							soi.address3_billing = i["address_billing"]["address3"]
							soi.address4_billing = i["address_billing"]["address4"]
							soi.address5_billing = i["address_billing"]["address5"]
							soi.city_billing = i["address_billing"]["city"]
							soi.country_billing = i["address_billing"]["country"]
							soi.post_code_billing = i["address_billing"]["post_code"]
							soi.phone_billing = i["address_billing"]["phone"]
							soi.phone2_billing = i["address_billing"]["phone2"]

							# shipping
							soi.first_name_shipping = i["address_shipping"]["first_name"]
							soi.last_name_shipping = i["address_shipping"]["last_name"]
							soi.address1_shipping = i["address_shipping"]["address1"]
							soi.address2_shipping = i["address_shipping"]["address2"]
							soi.address3_shipping = i["address_shipping"]["address3"]
							soi.address4_shipping = i["address_shipping"]["address4"]
							soi.address5_shipping = i["address_shipping"]["address5"]
							soi.city_shipping = i["address_shipping"]["city"]
							soi.country_shipping = i["address_shipping"]["country"]
							soi.post_code_shipping = i["address_shipping"]["post_code"]
							soi.phone_shipping = i["address_shipping"]["phone"]
							soi.phone2_shipping = i["address_shipping"]["phone2"]

							soi.total_amount = i["price"]
							soi.note = i["remarks"]

							soi.shipping_carrier = ""
							soi.tracking_no = ""
							soi.days_to_ship = i["promised_shipping_times"]

							child_client = LazopClient(url, appkey ,appSecret)
							child_request = LazopRequest('/order/items/get','GET')
							child_request.add_api_param('order_id', str(i["order_number"]))
							child_response = client.execute(child_request, access_token)
							
							print(child_response.type)
							print(child_response.body)


							if child_response.body["data"] :
								soi.item_detail = ""
								array_item = []
								temp_array_item = {}
								for a in child_response.body["data"] :

									# frappe.throw( a["recipient_address"]["name"])
									soi.currency = a["currency"]


									temp_array_item = {
										"item_sku" : a["sku"],
										"item_shop_sku" : a["shop_sku"],
										"item_name" : a["name"],
										"item_status" : a["status"],
										"item_item_price" : a["item_price"],
										"item_paid_price" : a["paid_price"],
										"item_warehouse_code" : a["warehouse_code"],
										"item_shipping_type" : a["shipping_type"],
										"item_shipping_provider_type" : a["shipping_provider_type"],
										"item_shipping_fee_original" : a["shipping_fee_original"],
										"item_is_digital" : a["is_digital"],
										
										"item_shipping_service_cost" : a["shipping_service_cost"],
										"item_tracking_code" : a["tracking_code"],
										"item_shipping_amount" : a["shipping_amount"],
										"item_reason_detail" : a["reason_detail"],
										"item_return_status" : a["return_status"],
										"item_shipment_provider" : a["shipment_provider"],
										"item_voucher_amount" : a["voucher_amount"],
										"item_digital_delivery_info" : a["digital_delivery_info"]
									}

									array_item.append(temp_array_item)
								soi.item_detail = str(array_item)

				docu.flags.ignore_permission = True
				docu.save()











@frappe.whitelist()
def get_order_list_lazada_manual():

	# pertama ambil dulu store nya

	get_store = frappe.db.sql("""
		SELECT ss.`name` 
		FROM `tabLazada Store` ss
		WHERE ss.`disable` = 0
		AND ss.`api_key` != ""
		AND ss.`api_secret` != ""
		AND ss.`access_token` != ""
	""")

	if get_store :
		for gs in get_store :

			count = 0

			# create timestamp
			# today_morning = today + " 00:00:00"
			# today_evening = today + " 23:59:59"

			time_from = ""
			time_to = ""

			today = str("2018-05-22")
			day_sebelumnya = str(add_days(utils.today(), -1));
			today_morning = today + "T00:00:00"
			today_evening = today + "T23:59:59"

			time_from = str(today_morning)
			time_to = str(today_evening)

			# time_from = int(time.mktime(datetime.datetime.strptime(str(today_morning), "%Y-%m-%d %H:%M:%S").timetuple()))
			# time_to = int(time.mktime(datetime.datetime.strptime(str(today_evening), "%Y-%m-%d %H:%M:%S").timetuple()))

			store_name = str(gs[0])

			lazada_setting = frappe.get_doc("Lazada Store", store_name)
			# shopee order name
			temp_name = "LAZADA|"+str(today)+"|"+str(gs[0])

			cari_data = frappe.get_value("Lazada Order", str(temp_name), "name")

			if cari_data : 

				docu = frappe.get_doc("Lazada Order", str(temp_name))

				if lazada_setting.disable == 0 :

					# get credential
					url = lazada_setting.url_store
					appkey = lazada_setting.api_key
					appSecret = lazada_setting.api_secret
					access_token = lazada_setting.access_token

					client = LazopClient(url, appkey ,appSecret)
					request = LazopRequest('/orders/get','GET')

					request.add_api_param('created_before', time_to)
					request.add_api_param('created_after', time_from)
					request.add_api_param('offset', '0')
					request.add_api_param('limit', '10')
					
					response = client.execute(request, access_token)
					print(response.type)
					print(response.body)

					if response.body :

						docu.lazada_order_list = []

						for i in response.body["data"]["orders"] :

							soi = docu.append('lazada_order_list', {})
							soi.order_id = i["order_number"]
							soi.order_status = i["statuses"][0]

							if i["customer_last_name"] :
								soi.customer = i["customer_first_name"] + " " + i["customer_last_name"]
							else :
								soi.customer = i["customer_first_name"]

							# billing
							soi.first_name_billing = i["address_billing"]["first_name"]
							soi.last_name_billing = i["address_billing"]["last_name"]
							soi.address1_billing = i["address_billing"]["address1"]
							soi.address2_billing = i["address_billing"]["address2"]
							soi.address3_billing = i["address_billing"]["address3"]
							soi.address4_billing = i["address_billing"]["address4"]
							soi.address5_billing = i["address_billing"]["address5"]
							soi.city_billing = i["address_billing"]["city"]
							soi.country_billing = i["address_billing"]["country"]
							soi.post_code_billing = i["address_billing"]["post_code"]
							soi.phone_billing = i["address_billing"]["phone"]
							soi.phone2_billing = i["address_billing"]["phone2"]

							# shipping
							soi.first_name_shipping = i["address_shipping"]["first_name"]
							soi.last_name_shipping = i["address_shipping"]["last_name"]
							soi.address1_shipping = i["address_shipping"]["address1"]
							soi.address2_shipping = i["address_shipping"]["address2"]
							soi.address3_shipping = i["address_shipping"]["address3"]
							soi.address4_shipping = i["address_shipping"]["address4"]
							soi.address5_shipping = i["address_shipping"]["address5"]
							soi.city_shipping = i["address_shipping"]["city"]
							soi.country_shipping = i["address_shipping"]["country"]
							soi.post_code_shipping = i["address_shipping"]["post_code"]
							soi.phone_shipping = i["address_shipping"]["phone"]
							soi.phone2_shipping = i["address_shipping"]["phone2"]

							soi.total_amount = i["price"]
							soi.note = i["remarks"]

							soi.shipping_carrier = ""
							soi.tracking_no = ""
							soi.days_to_ship = i["promised_shipping_times"]

							child_client = LazopClient(url, appkey ,appSecret)
							child_request = LazopRequest('/order/items/get','GET')
							child_request.add_api_param('order_id', str(i["order_number"]))
							child_response = client.execute(child_request, access_token)
							
							print(child_response.type)
							print(child_response.body)


							if child_response.body["data"] :
								soi.item_detail = ""
								array_item = []
								temp_array_item = {}
								for a in child_response.body["data"] :

									# frappe.throw( a["recipient_address"]["name"])
									soi.currency = a["currency"]


									temp_array_item = {
										"item_sku" : a["sku"],
										"item_shop_sku" : a["shop_sku"],
										"item_name" : a["name"],
										"item_status" : a["status"],
										"item_item_price" : a["item_price"],
										"item_paid_price" : a["paid_price"],
										"item_warehouse_code" : a["warehouse_code"],
										"item_shipping_type" : a["shipping_type"],
										"item_shipping_provider_type" : a["shipping_provider_type"],
										"item_shipping_fee_original" : a["shipping_fee_original"],
										"item_is_digital" : a["is_digital"],
										
										"item_shipping_service_cost" : a["shipping_service_cost"],
										"item_tracking_code" : a["tracking_code"],
										"item_shipping_amount" : a["shipping_amount"],
										"item_reason_detail" : a["reason_detail"],
										"item_return_status" : a["return_status"],
										"item_shipment_provider" : a["shipment_provider"],
										"item_voucher_amount" : a["voucher_amount"],
										"item_digital_delivery_info" : a["digital_delivery_info"]
									}

									array_item.append(temp_array_item)
								soi.item_detail = str(array_item)

				docu.flags.ignore_permission = True
				docu.save()

			else :
				docu = frappe.new_doc("Lazada Order")
				docu.store = store_name
				docu.date = str(today)
				docu.general_information = """ 
					Date From {} s/d {}
					
				""".format(today_morning, today_evening)

				if lazada_setting.disable == 0 :

					# get credential
					url = lazada_setting.url_store
					appkey = lazada_setting.api_key
					appSecret = lazada_setting.api_secret
					access_token = lazada_setting.access_token

					client = LazopClient(url, appkey ,appSecret)
					request = LazopRequest('/orders/get','GET')

					request.add_api_param('created_before', time_to)
					request.add_api_param('created_after', time_from)
					request.add_api_param('offset', '0')
					request.add_api_param('limit', '10')
					
					response = client.execute(request, access_token)
					print(response.type)
					print(response.body)

					if response.body :

						docu.lazada_order_list = []

						for i in response.body["data"]["orders"] :

							soi = docu.append('lazada_order_list', {})
							soi.order_id = i["order_number"]
							soi.order_status = i["statuses"][0]

							if i["customer_last_name"] :
								soi.customer = i["customer_first_name"] + " " + i["customer_last_name"]
							else :
								soi.customer = i["customer_first_name"]

							# billing
							soi.first_name_billing = i["address_billing"]["first_name"]
							soi.last_name_billing = i["address_billing"]["last_name"]
							soi.address1_billing = i["address_billing"]["address1"]
							soi.address2_billing = i["address_billing"]["address2"]
							soi.address3_billing = i["address_billing"]["address3"]
							soi.address4_billing = i["address_billing"]["address4"]
							soi.address5_billing = i["address_billing"]["address5"]
							soi.city_billing = i["address_billing"]["city"]
							soi.country_billing = i["address_billing"]["country"]
							soi.post_code_billing = i["address_billing"]["post_code"]
							soi.phone_billing = i["address_billing"]["phone"]
							soi.phone2_billing = i["address_billing"]["phone2"]

							# shipping
							soi.first_name_shipping = i["address_shipping"]["first_name"]
							soi.last_name_shipping = i["address_shipping"]["last_name"]
							soi.address1_shipping = i["address_shipping"]["address1"]
							soi.address2_shipping = i["address_shipping"]["address2"]
							soi.address3_shipping = i["address_shipping"]["address3"]
							soi.address4_shipping = i["address_shipping"]["address4"]
							soi.address5_shipping = i["address_shipping"]["address5"]
							soi.city_shipping = i["address_shipping"]["city"]
							soi.country_shipping = i["address_shipping"]["country"]
							soi.post_code_shipping = i["address_shipping"]["post_code"]
							soi.phone_shipping = i["address_shipping"]["phone"]
							soi.phone2_shipping = i["address_shipping"]["phone2"]

							soi.total_amount = i["price"]
							soi.note = i["remarks"]

							soi.shipping_carrier = ""
							soi.tracking_no = ""
							soi.days_to_ship = i["promised_shipping_times"]

							child_client = LazopClient(url, appkey ,appSecret)
							child_request = LazopRequest('/order/items/get','GET')
							child_request.add_api_param('order_id', str(i["order_number"]))
							child_response = client.execute(child_request, access_token)
							
							print(child_response.type)
							print(child_response.body)


							if child_response.body["data"] :
								soi.item_detail = ""
								array_item = []
								temp_array_item = {}
								for a in child_response.body["data"] :

									# frappe.throw( a["recipient_address"]["name"])
									soi.currency = a["currency"]


									temp_array_item = {
										"item_sku" : a["sku"],
										"item_shop_sku" : a["shop_sku"],
										"item_name" : a["name"],
										"item_status" : a["status"],
										"item_item_price" : a["item_price"],
										"item_paid_price" : a["paid_price"],
										"item_warehouse_code" : a["warehouse_code"],
										"item_shipping_type" : a["shipping_type"],
										"item_shipping_provider_type" : a["shipping_provider_type"],
										"item_shipping_fee_original" : a["shipping_fee_original"],
										"item_is_digital" : a["is_digital"],
										
										"item_shipping_service_cost" : a["shipping_service_cost"],
										"item_tracking_code" : a["tracking_code"],
										"item_shipping_amount" : a["shipping_amount"],
										"item_reason_detail" : a["reason_detail"],
										"item_return_status" : a["return_status"],
										"item_shipment_provider" : a["shipment_provider"],
										"item_voucher_amount" : a["voucher_amount"],
										"item_digital_delivery_info" : a["digital_delivery_info"]
									}

									array_item.append(temp_array_item)
								soi.item_detail = str(array_item)

				docu.flags.ignore_permission = True
				docu.save()