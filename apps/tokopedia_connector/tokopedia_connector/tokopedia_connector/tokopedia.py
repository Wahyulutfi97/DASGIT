# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import json
import requests
from datetime import date
from frappe.utils import flt, rounded, add_months,add_days, nowdate, getdate
import time
import datetime


@frappe.whitelist()
def get_etalase():
	datas=frappe.db.get_list('Tokopedia Setting',filters={'enable_sync': '1'},fields=['app_id','shop_name','token','shop_id'])
	url = "https://fs.tokopedia.net/inventory/v1/fs/15209/product/etalase?shop_id="+datas[0]['shop_id']
	payload={}
	headers = {
		'Authorization': 'Bearer '+ datas[0]['token']
	}
	response = requests.request("GET", url, headers=headers, data=payload)
	etalse = json.loads(response.text)
	return(etalse)

@frappe.whitelist()
def get_etalase2():
	frappe.msgprint("bisaaaa")
	datas=frappe.db.get_list('Tokopedia Setting',filters={'enable_sync': '1'},fields=['app_id','shop_name','token','shop_id'])
	url = "https://fs.tokopedia.net/inventory/v1/fs/15209/product/etalase?shop_id="+datas[0]['shop_id']
	payload={}
	headers = {
		'Authorization': 'Bearer '+ datas[0]['token']
	}
	response = requests.request("GET", url, headers=headers, data=payload)
	etalse = json.loads(response.text)
	for i in etalse['data']['etalase']:
		get_e = frappe.get_value("List Etalase",{"name" : i['etalase_id']}, "name")
		if get_e:
			frappe.msgprint("Etalase Sudah ada")
		else:
			doc = frappe.new_doc('List Etalase')
			doc.id = i['etalase_id']
			doc.etalase = i['etalase_name']

			doc.flags.ignore_permission = True
			doc.save()



@frappe.whitelist()
def get_cat_manual():
	datas=frappe.db.get_list('Tokopedia Setting',filters={'enable_sync': '1'},fields=['app_id','shop_name','token','shop_id'])
	datac =frappe.db.get_list('List Category Tokopedia',filters={'docstatus': '0'},fields=['keyword'])
	#datac[0]['keyword']
	#doc = frappe.new_doc('Item')
	url = "https://fs.tokopedia.net/inventory/v1/fs/"+datas[0]['app_id']+"/product/category"
	payload={}
	headers = {
		'Authorization': 'Bearer '+ datas[0]['token']
	}
	response = requests.request("GET", url, headers=headers, data=payload)
	cat = json.loads(response.text)
	return(cat)

@frappe.whitelist()
def get_cat_manual2():
	frappe.msgprint("bisa")
	datas=frappe.db.get_list('Tokopedia Setting',filters={'enable_sync': '1'},fields=['app_id','shop_name','token','shop_id'])
	datac =frappe.db.get_list('List Category Tokopedia',filters={'docstatus': '0'},fields=['keyword'])
	#datac[0]['keyword']
	#doc = frappe.new_doc('Item')
	url = "https://fs.tokopedia.net/inventory/v1/fs/"+datas[0]['app_id']+"/product/category"
	payload={}
	headers = {
		'Authorization': 'Bearer '+ datas[0]['token']
	}
	response = requests.request("GET", url, headers=headers, data=payload)
	cat = json.loads(response.text)
	data = []
	data = cat['data']['categories']
	data2 = data[0]['child']
	# list child
	for i in data2[2:15]:
		for j in i['child']:
			doc = frappe.get_doc("Child Tokopedia",i['id'])
			row = doc.append('list_child', {})
			row.id= j['id']
			row.child_name= j['name']

			doc.flags.ignore_permission = True
			doc.save()

	# child 1
	# for i in data[0]['child']:
	# 	doc = frappe.new_doc('Child Tokopedia')
	# 	doc.id_parent = 8
	# 	doc.id = i['id']
	# 	doc.name_child = i['name']
		
	# 	doc.flags.ignore_permission = True
	# 	doc.save()
	
	#induk
	# for i in cat['data']['categories']:
	# 	doc = frappe.new_doc('List Category Tokopedia')
	# 	doc.id = i['id']
	# 	doc.kategori = i['name']
		
	# 	doc.flags.ignore_permission = True
	# 	doc.save()

	


@frappe.whitelist()
def get_cat(doc,method):
	datas=frappe.db.get_list('Tokopedia Setting',filters={'enable_sync': '1'},fields=['app_id','shop_name','token','shop_id'])
	#datac =frappe.db.get_list('List Category Tokopedia',filters={'docstatus': '0'},fields=['keyword'])
	#datac[0]['keyword']
	doc = frappe.new_doc('Item')
	url = "https://fs.tokopedia.net/inventory/v1/fs/"+datas[0]['app_id']+"/product/category?keyword=%"+doc.keyword+"%"
	payload={}
	headers = {
		'Authorization': 'Bearer '+ datas[0]['token']
	}
	response = requests.request("GET", url, headers=headers, data=payload)
	cat = json.loads(response.text)
	return(cat)

@frappe.whitelist()
def gen_token():
	datas=frappe.db.get_list('Tokopedia Setting',filters={'enable_sync': '1'},fields=['name','basic_base_64'])
	for i in datas:
		url = "https://accounts.tokopedia.com/token?grant_type=client_credentials"
		payload={}
		headers = {
			'Authorization': 'Basic '+i['basic_base_64'],
	  	  	'Content-Length': '0',
	    	'User-Agent': 'PostmanRuntime/7.17.1'
		}
		response = requests.request("POST", url, headers=headers, data=payload)
		tokens = json.loads(response.text)
		get_token = frappe.get_doc("Tokopedia Setting",i['name'])
		get_token.token = tokens['access_token']
		
		get_token.flags.ignore_permission = True
		get_token.save()

@frappe.whitelist()
def get_data():
	frappe.msgprint("coba")
	datas=frappe.db.get_list('Tokopedia Setting',filters={'enable_sync': '1'},fields=['app_id','shop_name','token','shop_id'])
	for i in datas:
		today = date.today()
		back_date = str(add_days(today, -2))
		start_date = str(add_days(today, 1))
		from_date = back_date+ " 00:00:00"
		to_date = start_date+ " 00:00:00"
		time_from = int(time.mktime(datetime.datetime.strptime(str(from_date), "%Y-%m-%d %H:%M:%S").timetuple()))
		time_to = int(time.mktime(datetime.datetime.strptime(str(to_date), "%Y-%m-%d %H:%M:%S").timetuple()))
		strtime_from = str(time_from)
		strtime_to = str(time_to)
		url = "https://fs.tokopedia.net/v1/fs/"+i['app_id']+"/fulfillment_order"
		#url = "https://fs.tokopedia.net/v2/order/list?fs_id="+i['app_id']+"&shop_id="+i['shop_id']+"&from_date="+ strtime_from +"&to_date="+ strtime_to +"&page=1&per_page=10"
		payload={}
		headers = {
		  'Authorization': 'Bearer '+ i['token']
		}
		response = requests.request("GET", url, headers=headers, data=payload)
		datao = json.loads(response.text)

		for x in datao['data']['order_data']:
			get_order = frappe.get_value("Tokopedia Orders",{"name" : str(x['order']['order_id'])}, "name")
			urlsave = "https://fs.tokopedia.net/v2/fs/"+i['app_id']+"/order?order_id=" + str(x['order']['order_id'])
			payloadssave={}
			headers = {
	  			'Authorization': 'Bearer '+ i['token']
			}
			r = requests.request("GET", urlsave, headers=headers, data=payloadssave)
			datasave = json.loads(r.text)
			if get_order :
				doc = frappe.get_doc("Tokopedia Orders",get_order)
				status = datasave['data']['order_status']
				doc.days_to_ship = datasave['data']['order_info']['delivered_age_day']
				if status == 0:
					doc.order_status = 'Seller cancel order'
				if status == 10:
					doc.order_status = 'Order Pending Replacement'
				if status == 100:
					doc.order_status = 'Pending order'
				if status == 103:
					doc.order_status = 'Wait for payment confirmation from third party'
				if status == 220:
					doc.order_status = 'Payment verified, order ready to process'
				if status == 400:
					doc.order_status = 'Seller accept order'
				if status == 450:
					doc.order_status = 'Waiting for pickup'
				if status == 500:
					doc.order_status = 'Order shipment'
				if status == 520:
					doc.order_status = 'Invalid shipment reference number (AWB)'
				if status == 600:
					doc.order_status = 'Order delivered'
				if status == 700:
					doc.order_status = 'Order finished'
				
				doc.flags.ignore_permission = True
				doc.save()
			else :
				doc = frappe.new_doc('Tokopedia Orders')
				doc.order_id = str(x['order']['order_id'])
				doc.marketplace = "Tokopedia"
				doc.shop_name = i['shop_name']
				status = datasave['data']['order_status']
				if status == 0:
					doc.order_status = 'Seller cancel order'
				if status == 10:
					doc.order_status = 'Order Pending Replacement'
				if status == 100:
					doc.order_status = 'Pending order'
				if status == 103:
					doc.order_status = 'Wait for payment confirmation from third party'
				if status == 220:
					doc.order_status = 'Payment verified, order ready to process'
				if status == 400:
					doc.order_status = 'Seller accept order'
				if status == 450:
					doc.order_status = 'Waiting for pickup'
				if status == 500:
					doc.order_status = 'Order shipment'
				if status == 520:
					doc.order_status = 'Invalid shipment reference number (AWB)'
				if status == 600:
					doc.order_status = 'Order delivered'
				if status == 700:
					doc.order_status = 'Order finished'

				doc.days_to_ship = datasave['data']['order_info']['delivered_age_day']
				doc.customer = datasave['data']['buyer_info']['buyer_id']
				doc.customer_name = datasave['data']['buyer_info']['buyer_fullname']
				alamat = datasave['data']['order_info']['destination']['address_street']+' '+datasave['data']['order_info']['destination']['address_city']+', '+datasave['data']['order_info']['destination']['address_district']+', '+datasave['data']['order_info']['destination']['address_postal']+', '+datasave['data']['order_info']['destination']['address_province']
				doc.recipient_address = alamat
				doc.recipient_phone = datasave['data']['order_info']['destination']['receiver_phone']
				doc.recipient_city = datasave['data']['order_info']['destination']['address_city']
				item = frappe.get_list("Tokopedia Orders Item",{"parent" : get_order},"parent")

				if len(item) == 0 :
					for i in datasave['data']['order_info']['order_detail']:
						row = doc.append('items', {})
						# if '-' in i['product_name']:
						# 	name = i['product_name'].split("-")
						# 	variant = i['product_name'].split("-")
						# 	row.item_name = name[0]
						# 	row.variant = variant[1]
						# else :
						# 	row.item_name = i['product_name']
						row.item_name = i['product_name']
						row.variant = i['product_name']
						row.item_sku = i['sku']
						row.qty = i['quantity']
						row.price_list_rate= i['product_price']
						row.rate = i['subtotal_price']

				if datasave['data']['promo_order_detail']['summary_promo'] :
					for p in datasave['data']['promo_order_detail']['summary_promo']:
						get_promo = frappe.get_value("List Promo",{"name1" : p['name'],"parent" : get_order}, "name1")
						if get_promo:
							frappe.msgprint("Promo Name Sudah ada")
						else :
							row = doc.append('list_promo', {})
							row.name1=p['name']
							row.type=p['type']
							row.cashback_points=p['cashback_points']
							row.cashback_amount=p['cashback_amount']

				doc.total_cashback= datasave['data']['promo_order_detail']['total_cashback']
				doc.currency = "IDR"
				doc.total_amount = datasave['data']['item_price']
				doc.shipping_carrier = datasave['data']['order_info']['shipping_info']['logistic_name']
				doc.estimated_shipping_fee = datasave['data']['order_info']['shipping_info']['shipping_price']
				doc.insurance_price = datasave['data']['order_info']['shipping_info']['insurance_price']
				doc.voucher_applied = datasave['data']['payment_info']['voucher_code']
				doc.additional_discount = datasave['data']['payment_info']['discount_amount']
				doc.tracking_no = datasave['data']['order_info']['shipping_info']['awb']
				#doc.grand_total = int(datasave['data']['order_info']['shipping_info']['shipping_price']) + int(datasave['data']['item_price']) - int(datasave['data']['payment_info']['discount_amount'])

				doc.flags.ignore_permission = True
				doc.save()

@frappe.whitelist()
def get_product():
	datas=frappe.db.get_list('Tokopedia Setting',filters={'enable_sync': '1'},fields=['app_id','shop_name','token','shop_id'])
	url = "https://fs.tokopedia.net/v2/products/fs/"+datas[0]['app_id']+"/1/20"
	payload={}
	headers = {
    	'Authorization': 'Bearer '+ datas[0]['token']
    }
	r_product = requests.request("GET", url, headers=headers, data=payload)
	data_p = json.loads(r_product.text)
	for i in data_p['data']:
		get_p = frappe.get_value("Item",{"item_code" : p['sku']}, "item_code")
		if get_p:
			frappe.msgprint("Item Sudah ada")
		else:
			url = "https://fs.tokopedia.net/inventory/v1/fs/"+datas[0]['app_id']+"/product/info?product_id="+str(i['product_id'])
			headers = {
  				'Authorization': 'Bearer '+datas[0]['token']
			}
			response = requests.request("GET", url, headers=headers, data=payload)
			detail_p = json.loads(response.text)
			
			doc = frappe.new_doc('Item')
			doc.item_code = p['sku']
			doc.item_name = detail_p['data'][0]['basic']['name']
			doc.item_group = "Tokopedia"
			doc.stock_uom ="Pcs"
			doc.opening_stock = detail_p['data'][0]['stock']['value']
			doc.standard_rate = detail_p['data'][0]['price']['value']
			doc.description = detail_p['data'][0]['basic']['shortDesc']
			doc.weight_per_unit = detail_p['data'][0]['weight']['value']
			
			if detail_p['data'][0]['weight']['unit'] == 1:
				doc.weight_uom ='GR'
			else :
				doc.weight_uom ='Kg'
			
			doc.image = detail_p['data'][0]['pictures'][0]['ThumbnailURL']
			doc.default_material_request_type="Purchase"
			row=doc.append('uoms', {})
			row.uom="Pcs"
			row.conversion_factor=1
			row_i=doc.append('item_defaults', {})
			row_i.company="Demo"
			row_i.default_warehouse="Stores - D"
			row_i.income_account="4110.000 - Penjualan - D"


			#doc.list_category = detail_p['data'][0]['categoryTree'][0]['name']
			#for p in detail_p['data'][0]['categoryTree']:

			if detail_p['data'][0]['basic']['condition'] == 1:
				doc.condition_item ='NEW'
			else :
				doc.condition_item ='USED'

			if detail_p['data'][0]['basic']['status'] == 1:
				doc.status_item ='LIMITED'

			doc.is_sync_tokopedia = 1

			if detail_p['data'][0]['basic']['mustInsurance'] == True:
				doc.is_must_insurance = 1
			else :
				doc.is_must_insurance = 0

			doc.min_order = detail_p['data'][0]['extraAttribute']['minOrder']

			doc.etalse = detail_p['data'][0]['menu']['name']+"-"+['data'][0]['menu']['id']

			doc.flags.ignore_permission=True
			doc.save()

			# price = frappe.new_doc('Item Price')
			# price.item_code = str(detail_p['data'][0]['basic']['productID'])
			# price.price_list = "Standard Selling"
			# price.selling = 1
			# price.price_list_rate = detail_p['data'][0]['price']['value']

			# price.flags.ignore_permission=True
			# price.save()


@frappe.whitelist()
def crate_product():
	datas=frappe.db.get_list('Tokopedia Setting',filters={'enable_sync': '1'},fields=['app_id','shop_name','token','shop_id'])
	url = "https://fs.tokopedia.net/v2/products/fs/"+datas[0]['app_id']+"/1/20"
	payload={}
	headers = {
    	'Authorization': 'Bearer '+ datas[0]['token']
    }
	r_product = requests.request("GET", url, headers=headers, data=payload)
	data_p = json.loads(r_product.text)
	#data_is = frappe.db.get_list('Item',filters={'disabled': 0,"item_group": "Shopee"},fields=['name','item_code','item_name','description','image'])
	data_i = frappe.db.get_list('Item',filters={'disabled': 0,"item_group": "Tokopedia","is_sync_tokopedia": "1"},fields=['*'])
	
	for p in data_p['data']:
		for i in data_i:
			#frappe.msgprint(p['sku']+"sudah ada - "+str(p['product_id']))
			if i['item_code'] == p['sku']:
				frappe.msgprint(i['item_code']+"-"+str(p['product_id']))

				if '-' in i['list_category']:
					id_cat = i['list_category'].split("-")
					cat_id = int(id_cat[1])

				if '-' in i['etalase']:
					id_etalase = i['etalase'].split("-")

				if i['is_free_return'] == 0:
					f_return = False
				else :
					f_return = True

				if i['is_must_insurance'] == 0:
					insurance = False
				else :
					insurance = True

				url = "https://fs.tokopedia.net/v2/products/fs/"+datas[0]['app_id']+"/edit?shop_id="+datas[0]['shop_id']
				payload = json.dumps({
				"products": [
			    {
			      "id":p['product_id'],
			      "name": i['item_name'], # karakter tidak boleh labih dari 70 tidak boleh sama
			      "condition": i['condition_item'],
			      "description": i['description'],
			      "sku": i['item_code'], #tidak boleh ada spasi
			      "price": int(i['standard_rate']),
			      "status": i['status_item'],
			      "stock": int(i['opening_stock']),
			      "min_order": i['min_order'],
			      "category_id": cat_id,
			      "price_currency": i['currency_item_tokopedia'],
			      "weight": int(i['weight_per_unit']),
			      "weight_unit": i['weight_uom'],
			      "is_free_return": f_return,
			      "is_must_insurance": insurance,
			      "dimension": {
			        "height": float(i['height']),
			        "width":  float(i['width']),
			        "length":  float(i['length'])
			      },
			      "custom_product_logistics": [],
			      "annotations": ["1"],
			      "etalase": {
			        "id": int(i['id_etalase']) #kode etalase
			      },
			      "pictures": [
			        {
			          "file_path": frappe.utils.get_url()+i['gambar_utama']
			        	#i['image']
			        }
			      ],
			      "wholesale": [],
			      "preorder": {},
			      "videos": []
				 }
				]
				})

				headers = {
					'Authorization': 'Bearer '+datas[0]['token'],
					'Content-Type': 'application/json'
				}
				
				response = requests.request("PATCH", url, headers=headers, data=payload)
				# hasil1 = json.loads(response.text)
				# return(hasil1)
				print(response.text)

			else :
				#untuk tambah data
				for i in data_i:
					get_price = frappe.get_value("Item Price",{"price_list" : "Standard Selling","item_code": i['item_code']}, "price_list_rate")
					
					if '-' in i['item_name']:
						name = i['item_name'].split("-")

					if '-' in i['list_category']:
						id_cat = i['list_category'].split("-")
						cat_id = int(id_cat[1])

					if '-' in i['etalase']:
						id_etalase = i['etalase'].split("-")

					if i['is_free_return'] == 0:
						f_return = False
					else :
						f_return = True

					if i['is_must_insurance'] == 0:
						insurance = False
					else :
						insurance = True
					
					url = "https://fs.tokopedia.net/v3/products/fs/"+datas[0]['app_id']+"/create?shop_id="+datas[0]['shop_id']
					payload = json.dumps({
					"products": [
				    {
				      "name": i['item_name'], # karakter tidak boleh labih dari 70 tidak boleh sama
				      "condition": i['condition_item'],
				      "description": i['description'],
				      "sku": i['item_code'], #tidak boleh ada spasi
				      "price": int(i['standard_rate']),
				      "status": i['status_item'],
				      "stock": int(i['opening_stock']),
				      "min_order": i['min_order'],
				      "category_id": cat_id,
				      "price_currency": i['currency_item_tokopedia'],
				      "weight": int(i['weight_per_unit']),
				      "weight_unit": i['weight_uom'],
				      "is_free_return": f_return,
				      "is_must_insurance": insurance,
				      "dimension": {
				        "height": float(i['height']),
				        "width":  float(i['width']),
				        "length":  float(i['length'])
				      },
				      "custom_product_logistics": [],
				      "annotations": ["1"],
				      "etalase": {
				        "id": int(i['id_etalase']) #kode etalase
				      },
				      "pictures": [
				        {
				          "file_path": frappe.utils.get_url()+i['gambar_utama']
				        	#i['image']
				        }
				      ],
				      "wholesale": [],
				      "preorder": {},
				      "videos": []
					 }
					]
					})

					headers = {
						'Authorization': 'Bearer '+datas[0]['token'],
						'Content-Type': 'application/json'
					}
					
					response = requests.request("POST", url, headers=headers, data=payload)
					#hasil = json.loads(response.text)
					# return(hasil)
					print(response.text)
