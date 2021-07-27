# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "marketplace_integration"
app_title = "Marketplace Integration"
app_publisher = "DAS"
app_description = "Marketplace Integration"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "digitalasiasolusindo@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/marketplace_integration/css/marketplace_integration.css"
# app_include_js = "/assets/marketplace_integration/js/marketplace_integration.js"

# include js, css files in header of web template
# web_include_css = "/assets/marketplace_integration/css/marketplace_integration.css"
# web_include_js = "/assets/marketplace_integration/js/marketplace_integration.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "marketplace_integration.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "marketplace_integration.install.before_install"
# after_install = "marketplace_integration.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "marketplace_integration.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
	# "all": [
	# 	"marketplace_integration.tasks.all"
	# ],
	"daily": [
		"marketplace_integration.marketplace_integration.doctype.tokopedia_store_setting.tokopedia_store_setting.gen_token",
		"marketplace_integration.marketplace_integration.doctype.lazada_store_setting.lazada_store_setting.create_access_token_daily"
	],
	"hourly": [
		"marketplace_integration.marketplace_integration.doctype.shopee_method.shopee_order_tiap_jam",
		"marketplace_integration.marketplace_integration.doctype.tokopedia_method.tokopedia_order_tiap_jam",
	],
	# "weekly": [
	# 	"marketplace_integration.tasks.weekly"
	# ]
	# "monthly": [
	# 	"marketplace_integration.tasks.monthly"
	# ]
}

# Testing
# -------

# before_tests = "marketplace_integration.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "marketplace_integration.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "marketplace_integration.task.get_dashboard_data"
# }

