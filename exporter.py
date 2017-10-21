from pysnow.exceptions import NoResults
import json
import os
import pysnow

user = os.environ.get('SNOW_USER')
password = os.environ.get('SNOW_PASS')
instance = os.environ.get('SNOW_INSTANCE')


# key name is table and value is key of that table where the associated sys_id is located
tables = {
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

# export only one item (for testing purposes)
record = request.get_multiple(order_by=['-created-on']).next()
sys_id = record['sys_id']
export = {'sc_cat_item': [record]}

# Name all the related lists (a.k.a. export related records from other tables)
for table_name, sysid_key in tables.iteritems():
    try:
        query = s.query(table=table_name, query={sysid_key: sys_id})
        for record in query.get_multiple():
            if not table_name in export:
                export[table_name] = []
            export[table_name].append(record)
    except NoResults:
        # Query yielded no results so just ignore it
        pass

catalogID = [] #done
categoryID = [] #done
vsrelID = []
vsID = []
vID = []
qcID = [] #done
uipID = []
actID = [] #done
csID = []

# Query for Catalogs
if 'sc_cat_item_catalog' in export:
    for catalog in export['sc_cat_item_catalog']:
        catalogID.append(catalog['sc_catalog']['sys_id'])

# Query for Categories
if 'sc_cat_item_category' in export:
    for category in export['sc_cat_item_category']:
        categoryID.append(category['sc_category']['sys_id'])

# Query for variables to get question choices
if 'item_option_new' in export:
    for item in export['item_option_new']:
        try:
            # Query for question choices
            query = s.query(table='question_choice', query={'question': item['sys_id']})
            for record in query.get_multiple():
                qcID.append(record['sys_id'])
        except NoResults:
            # Query yielded no results so just ignore it
            pass

# Query for ui catalog ui policies to get policy actions
if 'catalog_ui_policy' in export:
    for catpol in export['catalog_ui_policy']:
        try:
            # Query for ui policy actions
            query = s.query(table='catalog_ui_policy_action', query={'ui_policy': item['sys_id']})
            for record in query.get_multiple():
                actID.append(record['sys_id'])
        except NoResults:
            # Query yielded no results so just ignore it
            pass

# Query for variable set relationships

print json.dumps(export)
