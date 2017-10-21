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

# What is exported?

In addition to catalog items, the following records related to the exported
catalog item is also exported:

- Variables (including question choices)
- Variable sets (including associated variables, client scripts, and UI
  policies)
- Client scripts
- UI policies
- Additional categories
- Approved by user and group
- Available for/Not Available for lists
- Order guide rule base

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
    python export.py | python -m json.tool > dump.json

# Usage

```
ServiceNow ServiceCatalog Exporter

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
  --item=<sys_id>        Will export a single catalog item with the matching sys_id.  Accepts a CSV.
  --catalog=<sys_id>     Specify a catalog to limit --full.
  --instance=<instance>  The ServiceNow instance to export from.  Overrides the SNOW_INSTANCE environment variable.  Accepts a CSV.
  -o, --output=<file>    Dump the export to a file instead of stdout.
```

# License

[MIT License](LICENSE.txt)

[1]: https://www.servicenowguru.com/system-definition/exporting-service-catalog-items-step/
