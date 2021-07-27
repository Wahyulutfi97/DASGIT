// Copyright (c) 2021, DAS and contributors
// For license information, please see license.txt

/*frappe.ui.form.on('List Category Tokopedia', {
	// refresh: function(frm) {

	// }
});
*/

frappe.ui.form.on('List Category Tokopedia','refresh',function(frm) {
	 //refresh: function(frm) {
	 	frm.add_custom_button(__('Get Data'), function () {
       		console.log( 'test') ;
       		frappe.call({
			     method: "tokopedia_connector.tokopedia_connector.tokopedia.get_cat_manual",
			     args: {
                	doc: "List Category Tokopedia"
                	//cur_document: frm.doc.test_invoice
           		 },
			     callback: function(r) {
				     //console.log(r.message.data.categories);
				  	 var result = [];
				     //fulfillment_order
				     for (let i = 0;i < r.message.data.categories.length;i++) {
				     	//result.push(r.message.data.categories[i].name+"-"+r.message.data.categories[i].id)
				     	if (r.message.data.categories[i].child){
				     		for (let j = 0;j < r.message.data.categories[i].child.length;j++){
				     			if (r.message.data.categories[i].child[j].child){
				     				for (let k = 0;k < r.message.data.categories[i].child[j].child.length;k++){
				     					// console.log(r.message.data.categories[i].child[j].child[k].name)
				     					result.push(r.message.data.categories[i].child[j].child[k].name+"-"+r.message.data.categories[i].child[j].child[k].id)
				     				}
				     				
				     			}
				     			
				     		}
				     		
				     	}
				     	//console.log(r.message.data.categories[i].name)
				     }
				     console.log(result)
				     frm.set_df_property('list_category', 'options', result);
			 	}
			});
    	});

});