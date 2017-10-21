# ServiceNow ServiceCatalog Exporter

This script will interact with the APIs of a ServiceNow instance and export all
ServiceCatalog catalog items.  The exported items will include any table
extending the `sc_cat_item` `table…catalog` items, record producers, content
items, and order guides.

The idea for the logic of this exporter came from a JavaScript based exporter
created by [ServiceNow|Guru][1].

This builds on `SN|Guru` example by being able to export all items from the
ServiceCatatalog and not just a single item.

> TODO: create an importer.  So the export can be transferred to another
> ServiceNow instance.

# Prerequisites

- Python 2.7
- pip
- virtualenv

# Getting started

### Set up your environment

    cp env.sh.EXAMPLE env.sh

Edit `env.sh` and set `SNOW_USER`, `SNOW_PASS`, and `SNOW_INSTANCE` to your
user/password and instance hosted by servicenow.

### Instantiate your python environment

Instantiate your python environment and install prerequisite python packages.

    virtualenv -p python2.7 .venv
    source .venv/bin/activate
    pip install -U pip
    pip install -r requirements.txt

# Create your first dump

    # set environment variables
    source env.sh
    # dump a record and all associated records
    python export.py > dump.json


[1]: https://www.servicenowguru.com/system-definition/exporting-service-catalog-items-step/
