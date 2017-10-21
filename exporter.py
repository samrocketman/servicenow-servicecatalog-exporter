from pysnow import QueryBuilder
from pysnow.exceptions import NoResults
import json
import os
import pysnow

class Exporter:


    def __init__(self, snow, export):
        self.export = export
        self.snow = snow


    def export_record(self, table, record):
        if not table in export:
            export[table] = []
        export[table].append(record)


    def export_record_generator(self, table, query):
        try:
            request = self.snow.query(table=table, query=query)
            for record in request.get_multiple():
                self.export_record(table, record)
                yield
        except NoResults:
            pass


    def export_queried_records(self, table, query):
        try:
            request = self.snow.query(table=table, query=query)
            for record in request.get_multiple():
                self.export_record(table, record)
        except NoResults:
            pass


    def retrieve_full_record(self, record):
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

        self.export_record('sc_cat_item', record)
        sys_id = record['sys_id']

        # Name all the related lists (a.k.a. export related records from other tables)
        for table_name, sysid_key in tables.iteritems():
            self.export_queried_records(table_name, {sysid_key: sys_id})

        # Query for Catalogs
        catalogID = []
        if 'sc_cat_item_catalog' in export:
            for catalog in export['sc_cat_item_catalog']:
                catalogID.append(catalog['sc_catalog']['value'])
            self.export_queried_records('sc_catalog', str('sys_idIN%s' % ','.join(catalogID)))

        # Query for Categories
        categoryID = []
        if 'sc_cat_item_category' in export:
            for category in export['sc_cat_item_category']:
                categoryID.append(category['sc_category']['value'])
            self.export_queried_records('sc_category', str('sys_idIN%s' % ','.join(categoryID)))

        # Query for variables to get question choices
        if 'item_option_new' in export:
            for item in export['item_option_new']:
                # Query for question choices
                self.export_queried_records('question_choice', {'question': item['sys_id']})

        # Query for ui catalog ui policies to get policy actions
        if 'catalog_ui_policy' in export:
            for catpol in export['catalog_ui_policy']:
                # Query for ui policy actions
                self.export_queried_records('catalog_ui_policy_action', {'ui_policy': item['sys_id']})

        # Query for variable set relationships
        if 'io_set_item' in export:
            for vsrel in export['io_set_item']:
                vs = None
                try:
                    # Get the variable set
                    vs = self.snow.query(table='item_option_new_set', query={'sys_id': vsrel['variable_set']['value']}).get_one()
                    self.export_record('item_option_new_set', vs)
                except NoResults:
                    # Query yielded no results so skip
                    continue

                # Query for variables in the set
                for v in self.export_record_generator('item_option_new', {'variable_set': vs['sys_id']}):
                    # Query for variable question choices
                    if v:
                        self.export_queried_records('question_choice', {'question': v['sys_id']})

                # Query for ui policies in the set
                for uip in self.export_record_generator('catalog_ui_policy', {'variable_set': vs['sys_id']}):
                    # Query for ui policy actions
                    if uip:
                        self.export_queried_records('catalog_ui_policy_action', {'ui_policy': uip['sys_id']})

                # Query for client scripts in the set
                self.export_queried_records('catalog_script_client', {'variable_set': vs['sys_id']})

if __name__ == "__main__":
    user = os.environ.get('SNOW_USER')
    password = os.environ.get('SNOW_PASS')
    instance = os.environ.get('SNOW_INSTANCE')
    s = pysnow.Client(instance=instance, user=user, password=password)
    request = s.query(table='sc_cat_item', query={})
    export = {}

    exporter = Exporter(s, export)
    # export only one item (for testing purposes)
    record = request.get_multiple(order_by=['-created-on']).next()
    exporter.retrieve_full_record(record)

    print json.dumps(export)
