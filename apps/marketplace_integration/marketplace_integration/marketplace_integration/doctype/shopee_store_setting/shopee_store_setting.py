# -*- coding: utf-8 -*-
# Copyright (c) 2021, DAS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

from marketplace_integration.marketplace_integration.doctype.frappeclient import FrappeClient
from marketplace_integration.marketplace_integration.doctype.shopee_store_setting.shopee_connector.client import Client
from marketplace_integration.marketplace_integration.doctype.shopee_store_setting.shopee_connector.shopcategory import ShopCategory

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

class ShopeeStoreSetting(Document):
	
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
		# untuk live
		host = "https://partner.shopeemobile.com"
		# untuk test
		# host = "https://partner.test-stable.shopeemobile.com"
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

	def validate(self):
		if self.enable_sync :
			if self.shop_id and self.partner_id and self.partner_key :
				shopid = int(self.shop_id)
				partnerid = int(self.partner_id)
				api_key = str(self.partner_key)
				shopeeclient = Client(shopid, partnerid, api_key)

				result = shopeeclient.shop.get_shop_info()
				# frappe.throw(str(result))
				if result :
					
					self.shop_name = result["shop_name"]
					self.shop_region = result["country"]
					self.shop_status = result["status"]


def testing_get_shop():
	shopid = int("305288982")
	partnerid = int("2000675")
	api_key = str("9d56537cd047d03513cddede1fcd590a41de4ad94ac977e8da3c3ba2f5f25e60")
	shopeeclient = Client(shopid, partnerid, api_key)

	result = shopeeclient.order.get_order_escrow_detail(ordersn = "210617HJWYKMM5")
	frappe.throw(str(result))
	
@frappe.whitelist()
def enqueue_shopee_order():
	count = 0
	time_from = 0
	time_to = 0
	curr_date = "2021-06-22"
	today = str(curr_date)
	day_sebelumnya = str(add_days(curr_date, -1));
	today_morning = day_sebelumnya + " 17:00:00"
	today_evening = today + " 16:59:59"

	time_from = int(time.mktime(datetime.datetime.strptime(str(today_morning), "%Y-%m-%d %H:%M:%S").timetuple()))
	time_to = int(time.mktime(datetime.datetime.strptime(str(today_evening), "%Y-%m-%d %H:%M:%S").timetuple()))
	
	# get credential
	shopid = int("305288982")
	partnerid = int("2000675")
	api_key = str("9d56537cd047d03513cddede1fcd590a41de4ad94ac977e8da3c3ba2f5f25e60")
	shopeeclient = Client(shopid, partnerid, api_key)

	# di looping 5x
	pagination_entry = 100
	pagination_offset = 0
	temp_continue = True

	for looping in range(25) :
		if temp_continue == False :
			break

		elif temp_continue == True :
			result = shopeeclient.order.get_order_list(update_time_from = time_from, update_time_to = time_to, pagination_entries_per_page = pagination_entry, pagination_offset = pagination_offset)
			# frappe.throw(str(result))

			if result["orders"] :
				
				for i in result["orders"] :

					print(str(i["ordersn"]))

					# cari dulu apakah ada
					get_morder = frappe.get_value("Marketplace Order", {"name" : i["ordersn"]}, "name")

					# ada
					if get_morder :

						get_marketplace_order = frappe.get_doc("Marketplace Order", get_morder)

						if str(i["order_status"]=="UNPAID" or i["order_status"]=="READY_TO_SHIP" or i["order_status"]=="CANCELLED" or i["order_status"]=="COMPLETED" or i["order_status"]=="IN_CANCEL" or i["order_status"]=="TO_RETURN") :

							if get_marketplace_order.order_status != i["order_status"] :

								get_docu = frappe.get_doc("Marketplace Order", i["ordersn"])
								get_docu.order_status = i["order_status"]
								get_docu.marketplace = "Shopee"
								get_docu.store_name = "testing_shop"

								if i["order_status"] != "UNPAID" :
									get_docu.sudah_lunas = 1

								child_result = shopeeclient.order.get_order_detail(ordersn_list = [i["ordersn"]])
								if child_result["orders"] :
									for a in child_result["orders"] :
										get_docu.kurir = a["shipping_carrier"]
										get_docu.no_resi = a["tracking_no"]
										get_docu.batas_kirim = a["days_to_ship"]

								get_docu.flags.ignore_permission = True
								get_docu.save()


					# tidak ada
					else :
						new_docu = frappe.new_doc("Marketplace Order")
						new_docu.marketplace = "Shopee"
						new_docu.no_referensi = i["ordersn"]
						new_docu.order_status = i["order_status"]

						new_docu.store_name = "testing_shop"

						if i["order_status"] != "UNPAID" :
							new_docu.sudah_lunas = 1

						
						child_result = shopeeclient.order.get_order_detail(ordersn_list = [i["ordersn"]])
						result_escrow = shopeeclient.order.get_order_escrow_detail(ordersn = i["ordersn"])

						total_subtotal = 0
						total_diskon = 0

						if child_result["orders"] :
							for a in child_result["orders"] :

								new_docu.posting_date = str(time.localtime(a["create_time"]))

								new_docu.id_pelanggan = a["buyer_username"]
								new_docu.pelanggan = a["recipient_address"]["name"].replace(">","").replace("<","").replace("'","").replace('"',"")
								new_docu.nama_penerima = a["recipient_address"]["name"].replace(">","").replace("<","").replace("'","").replace('"',"")
								alamat_penerima = a["recipient_address"]["full_address"]
								patokan = ", ID,"
								if patokan in alamat_penerima :
									new_docu.alamat_penerima = alamat_penerima.replace(", ID,", ", Indonesia,")
								else :
									new_docu.alamat_penerima = alamat_penerima
								# new_docu.recipient_address = "Indonesia"
								new_docu.telp_penerima = a["recipient_address"]["phone"]
								new_docu.kota_penerima = a["recipient_address"]["city"]
								new_docu.keterangan = a["message_to_seller"]

								new_docu.total_amount = a["total_amount"]

								new_docu.kurir = a["shipping_carrier"]
								new_docu.no_resi = a["tracking_no"]
								new_docu.batas_kirim = a["days_to_ship"]
								
								variant_sku = ""
								item_sku = ""
								additional_discount = 0
								jumlah_item = 0
								jumlah_setelah_diskon = 0
								jumlah_sebelum_diskon = 0
								total_sebelum_diskon = 0
								total_setelah_diskon = 0
								harga_item_setelah_diskon = 0
								array_harga_itemnya = {}
								array_qty_itemnya = {}
								for j in a["items"] :
									
									if j["variation_sku"] :
										item_sku = str(j["variation_sku"])
									else :
										item_sku = str(j["item_sku"])
									
									new_child = new_docu.append("items", {})
									new_child.item_sku = str(item_sku)
									new_child.item_name = j["variation_name"]
									new_child.qty = str(j["variation_quantity_purchased"])
									new_child.harga = str(j["variation_original_price"])
									new_child.diskon = int(j["variation_original_price"]) - int(j["variation_discounted_price"])
									new_child.total = int(j["variation_discounted_price"]) * int(j["variation_quantity_purchased"])

									total_subtotal += int(j["variation_original_price"])
									total_diskon += (int(j["variation_original_price"]) - int(j["variation_discounted_price"]))


						new_docu.sub_total = total_subtotal
						new_docu.diskon = total_diskon
						new_docu.pajak = 0
						new_docu.diskon_lainnya = 0

						new_docu.ongkos_kirim = 0
						new_docu.asuransi = 0
						new_docu.biaya_lainnya = 0
						new_docu.potongan_biaya = 0
						

						if result_escrow :
							
							new_array_escrow = result_escrow["order"]["income_details"]
							new_docu.ongkos_kirim = int(new_array_escrow["final_shipping_fee"])

							new_docu.nilai_escrow = int(new_array_escrow["escrow_amount"])

							new_docu.potongan_biaya = int(new_array_escrow["commission_fee"]) + int(new_array_escrow["service_fee"]) + int(new_array_escrow["seller_transaction_fee"])


						new_docu.total = new_docu.sub_total - new_docu.diskon + new_docu.pajak - new_docu.diskon_lainnya + new_docu.ongkos_kirim + new_docu.asuransi + new_docu.biaya_lainnya - new_docu.potongan_biaya

						new_docu.flags.ignore_permission = True
						new_docu.save()

			temp_continue = result["more"]
			pagination_offset += 100
