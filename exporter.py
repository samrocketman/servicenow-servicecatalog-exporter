from pysnow import QueryBuilder
from pysnow.exceptions import NoResults
import json
import os
import pysnow


user = os.environ.get('SNOW_USER')
password = os.environ.get('SNOW_PASS')
instance = os.environ.get('SNOW_INSTANCE')

def export_record(export, table, record):
    if not table in export:
        export[table] = []
    export[table].append(record)

def export_record_generator(connector, export, table, query):
    try:
        request = connector.query(table=table, query=query)
        for record in request.get_multiple():
            export_record(export, table, record)
            yield
    except NoResults:
        pass

def export_queried_records(connector, export, table, query):
    try:
        request = connector.query(table=table, query=query)
        for record in request.get_multiple():
            export_record(export, table, record)
    except NoResults:
        pass

# key name is table and value is key of that table where the associated sc_cat_item.sys_id is located in the record
tables = {
    'item_option_new': 'cat_item',
    'catalog_script_client': 'cat_item',
    'catalog_ui_policy': 'catalog_item',
    'io_set_item': 'sc_cat_item',
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
    export_queried_records(s, export, table_name, {sysid_key: sys_id})

# Query for Catalogs
catalogID = []
if 'sc_cat_item_catalog' in export:
    for catalog in export['sc_cat_item_catalog']:
        catalogID.append(catalog['sc_catalog']['value'])
    export_queried_records(s, export, 'sc_catalog', str('sys_idIN%s' % ','.join(catalogID)))

# Query for Categories
categoryID = []
if 'sc_cat_item_category' in export:
    for category in export['sc_cat_item_category']:
        categoryID.append(category['sc_category']['value'])
    export_queried_records(s, export, 'sc_category', str('sys_idIN%s' % ','.join(categoryID)))

# Query for variables to get question choices
if 'item_option_new' in export:
    for item in export['item_option_new']:
        # Query for question choices
        export_queried_records(s, export, 'question_choice', {'question': item['sys_id']})

# Query for ui catalog ui policies to get policy actions
if 'catalog_ui_policy' in export:
    for catpol in export['catalog_ui_policy']:
        # Query for ui policy actions
        export_queried_records(s, export, 'catalog_ui_policy_action', {'ui_policy': item['sys_id']})

# Query for variable set relationships
if 'io_set_item' in export:
    for vsrel in export['io_set_item']:
        vs = None
        try:
            # Get the variable set
            vs = s.query(table='item_option_new_set', query={'sys_id': vsrel['variable_set']['value']}).get_one()
            if not 'item_option_new_set' in export:
                export['item_option_new_set'] = []
            export['item_option_new_set'].append(vs)
        except NoResults:
            # Query yielded no results so skip
            continue

        # Query for variables in the set
        for v in export_record_generator(s, export, 'item_option_new', {'variable_set': vs['sys_id']}):
            # Query for variable question choices
            if v:
                export_queried_records(s, export, 'question_choice', {'question': v['sys_id']})

        # Query for ui policies in the set
        for uip in export_record_generator(s, export, 'catalog_ui_policy', {'variable_set': vs['sys_id']}):
            # Query for ui policy actions
            if uip:
                export_queried_records(s, export, 'catalog_ui_policy_action', {'ui_policy': uip['sys_id']})

        # Query for client scripts in the set
        export_queried_records(s, export, 'catalog_script_client', {'variable_set': vs['sys_id']})

print json.dumps(export)
