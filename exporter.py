import os
import pysnow
import json

user = os.environ.get('SNOW_USER')
password = os.environ.get('SNOW_PASS')
instance = os.environ.get('SNOW_INSTANCE')


#key name is table and value is key of that table where the associated sys_id is located
tables_to_export = {
    'item_option_new': 'cat_item',
    'catalog_script_client': 'cat_item',
    'catalog_ui_policy': 'catalog_item',
    'sc_cat_item_category': 'sc_cat_item',
    'sc_cat_item_catalog': 'sc_cat_item',
    'sc_cat_item_user_criteria_mtom': 'sc_cat_item',
    'sc_cat_item_user_criteria_no_mtom': 'sc_cat_item',
    'sc_cat_item_group_mtom': 'sc_cat_item',
    'sc_cat_item_group_no_mtom': 'sc_cat_item',
    'sc_cat_item_company_mtom': 'sc_cat_item',
    'sc_cat_item_company_no_mtom': 'sc_cat_item',
    'sc_cat_item_dept_mtom': 'sc_cat_item',
    'sc_cat_item_dept_no_mtom': 'sc_cat_item',
    'sc_cat_item_location_mtom': 'sc_cat_item',
    'sc_cat_item_location_no_mtom': 'sc_cat_item',
    'sc_cat_item_user_mtom': 'sc_cat_item',
    'sc_cat_item_user_no_mtom': 'sc_cat_item',
    'sc_cat_item_app_group': 'sc_cat_item',
    'sc_cat_item_app_user': 'sc_cat_item',
    'sc_cat_item_guide_items': 'guide',
    'pc_vendor_cat_item': 'product_catalog_item'
}

s = pysnow.Client(instance=instance, user=user, password=password)
request = s.query(table='sc_cat_item', query={})

#export only one item (for testing purposes)
record = request.get_multiple(order_by=['-created-on']).next()
sys_id = record['sys_id']
export = {'sc_cat_item': [record]}

#instantiate a list of records for each table
for table_name, sysid_key in tables_to_export.iteritems():
    export[table_name] = []

for table_name, sysid_key in tables_to_export.iteritems():
    try:
        query = s.query(table=table_name, query={sysid_key: sys_id})
        for record in query.get_multiple():
            if record:
                export[table_name].append(record)
    except:
        #Query yielded no results
        pass

#only export tables which have records to export
print json.dumps(dict((k, v) for k, v in export.iteritems() if v))
