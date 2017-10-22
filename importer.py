#!/usr/bin/env python
"""ServiceNow ServiceCatalog Importer

This script will interact with the APIs of a ServiceNow instance and import
ServiceCatalog catalog items which were exported by exporter.py.

Usage: importer.py [-i <file> | --import=<file>] [--instance=<instance>]
       importer.py (-h | --help)
       importer.py --version

Options:

  -h --help              Show this screen.
  --version              Show version.
  -i, --import <file>    Import a dumped JSON file from exporter.py to a ServiceNow instance.
  --instance=<instance>  The ServiceNow instance to export from.  Overrides the SNOW_INSTANCE environment variable.
"""

import json
import os
import pysnow
import sys

class Importer:


    def __init__(self, snow):
        """
        Instantiates a new importer with a servicenow client from pysnow.Client and an export dictionary to write to a servicenow instance.
        """
        if not isinstance(snow, pysnow.Client):
            raise TypeError('snow must be an instance of %s' % pysnow.Client)
        self.snow = snow


    def write_multiple_records(self, table, records):
        """
        Writes multiple records (or a single record) to a ServiceNow instance.
        """
        payload = None
        if not isinstance(table, str):
            raise ValueError("table must be a str.")

        if isinstance(records, dict):
            # Single record
            payload = records

        if isinstance(records, list):
            # Multiple records
            payload = {"records": records}

        if not payload:
            raise ValueError("No records to send to service-now.")

        self.snow.insert(table=table, payload=payload)


if __name__ == '__main__':
    from docopt import docopt
    args = docopt(__doc__, version='ServiceNow ServiceCatalog Importer 0.3')

    user = os.environ.get('SNOW_USER')
    password = os.environ.get('SNOW_PASS')
    instance = args.get('--instance') or os.environ.get('SNOW_INSTANCE')
    s = pysnow.Client(instance=instance, user=user, password=password)
    export = {}

    importer = Importer(s)

    # Get the JSON dump
    if not args.get('--import'):
        export = json.load(sys.stdin)
    else:
        with open(args.get('--import')) as f:
            export = json.load(f)

    for table, records in export.iteritems():
        print >> sys.stderr, 'Importing records to %s' % table
        importer.write_multiple_records(str(table), records)
