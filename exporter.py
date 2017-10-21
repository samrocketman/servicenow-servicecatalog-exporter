#!/usr/bin/env python
"""ServiceNow ServiceCatalog Exporter

This script will interact with the APIs of a ServiceNow instance and export all
ServiceCatalog catalog items.  The exported items will include any table
extending the 'sc_cat_item' table items.  Including catalog items, record
producers, content items, and order guides.

By default only the most recently created catalog item will be exported.

Usage:
  exporter.py [--full] [--catalog=<sys_id>] [--instance=<instance>] [-o <file> | --output=<file>]
  exporter.py [--item=<sys_id>] [--instance=<instance>]
  exporter.py (-h | --help)
  exporter.py --version

Options:
  -h --help              Show this screen.
  --version              Show version.
  --full                 Export every ServiceCatalog catalog item.
  --item=<sys_id>        Will export a single catalog item with the matching sys_id.
  --catalog=<sys_id>     Specify a catalog to limit --full.
  --instance=<instance>  The ServiceNow instance to export from.  Overrides the SNOW_INSTANCE environment variable.
  -o, --output=<file>    Dump the export to a file instead of stdout.
"""

from pysnow import QueryBuilder
from pysnow.exceptions import NoResults
import json
import os
import pysnow
import sys

class Exporter:


    def __init__(self, snow, export, lock=None):
        """
        Instantiates a new exporter with a servicenow client from psnow.Client and an export dictionary to append entries.
        """
        if not isinstance(snow, pysnow.Client):
            raise TypeError('snow must be an instance of %s' % pysnow.Client)
        if not isinstance(export, dict):
            raise TypeError('export must be an instance of %s' % dict)
        self.snow = snow
        self.export = export


    def export_record(self, table, record):
        """
        Export a unique record based on sys_id to a table key.  This will append to the list of records for that table to be exported.
        """
        if not table in export:
            self.export[table] = []
        # only add unique records based on sys_id
        if not bool([r for r in self.export[table] if r.get('sys_id', '') == record['sys_id']]):
            self.export[table].append(record)


    def export_record_generator(self, table, query):
        """
        Similar to export_queried_records() but also offers a generator (similar to an iterator) to process each record.
        """
        try:
            request = self.snow.query(table=table, query=query)
            for record in request.get_multiple():
                self.export_record(table, record)
                yield
        except NoResults:
            pass


    def export_queried_records(self, table, query):
        """
        Queries the servicenow API and exports the matched records.
        """
        try:
            request = self.snow.query(table=table, query=query)
            for record in request.get_multiple():
                self.export_record(table, record)
        except NoResults:
            pass


    def retrieve_full_record(self, record):
        """
        Given a ServiceCatalog catalog item (a.k.a. sc_cat_item), this method will interate ServiceNow APIs to export the following related records.

        Will be exported:

        - Variables (including question choices)
        - Variable sets (including associated variables, client scripts, and UI policies)
        - Client scripts
        - UI policies
        - Additional categories
        - Approved by user and group
        - Available for/Not Available for lists
        - Order guide rule base

        This is based on https://www.servicenowguru.com/system-definition/exporting-service-catalog-items-step/
        """
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
            for catalog in self.export['sc_cat_item_catalog']:
                catalogID.append(catalog['sc_catalog']['value'])
            self.export_queried_records('sc_catalog', str('sys_idIN%s' % ','.join(catalogID)))

        # Query for Categories
        categoryID = []
        if 'sc_cat_item_category' in export:
            for category in self.export['sc_cat_item_category']:
                categoryID.append(category['sc_category']['value'])
            self.export_queried_records('sc_category', str('sys_idIN%s' % ','.join(categoryID)))

        # Query for variables to get question choices
        if 'item_option_new' in export:
            for item in self.export['item_option_new']:
                # Query for question choices
                self.export_queried_records('question_choice', {'question': item['sys_id']})

        # Query for ui catalog ui policies to get policy actions
        if 'catalog_ui_policy' in export:
            for catpol in self.export['catalog_ui_policy']:
                # Query for ui policy actions
                self.export_queried_records('catalog_ui_policy_action', {'ui_policy': item['sys_id']})

        # Query for variable set relationships
        if 'io_set_item' in export:
            for vsrel in self.export['io_set_item']:
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


if __name__ == '__main__':
    from docopt import docopt
    args = docopt(__doc__, version='ServiceNow ServiceCatalog Exporter 0.2')

    user = os.environ.get('SNOW_USER')
    password = os.environ.get('SNOW_PASS')
    instance = args.get('--instance') or os.environ.get('SNOW_INSTANCE')
    s = pysnow.Client(instance=instance, user=user, password=password)
    export = {}

    exporter = Exporter(s, export)

    if args.get('--full'):
        if args.get('--catalog'):
            query = 'sc_catalogsIN%s' % args.get('--catalog')
        else:
            query = {}
        request = s.query(table='sc_cat_item', query=query)
        for record in request.get_multiple(order_by=['-created-on']):
            print >> sys.stderr, 'Exporting: %s (sys_id: %s)' % (record['name'], record['sys_id'])
            exporter.retrieve_full_record(record)
    elif args.get('--item'):
        request = s.query(table='sc_cat_item', query='sys_idIN%s' %args.get('--item'))
        for record in request.get_multiple(order_by=['-created-on']):
            print >> sys.stderr, 'Exporting by sys_id: %s (sys_id: %s)' % (record['name'], record['sys_id'])
            exporter.retrieve_full_record(record)
    else:
        request = s.query(table='sc_cat_item', query={})
        record = request.get_multiple(order_by=['-created-on']).next()
        print >> sys.stderr, 'Exporting most recently created item: %s (sys_id: %s)' % (record['name'], record['sys_id'])
        exporter.retrieve_full_record(record)

    if args.get('--output'):
        with open(args.get('--output'), 'w') as f:
            json.dump(export, f)
    else:
        print json.dumps(export)
