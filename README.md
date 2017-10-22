# ServiceNow ServiceCatalog Exporter

This script will interact with the APIs of a ServiceNow instance and export all
ServiceCatalog catalog items.  The exported items will include any table
extending the `sc_cat_item` `table…catalog` items, record producers, content
items, and order guides.

The idea for the logic of this exporter came from a JavaScript based exporter
created by [ServiceNow|Guru][1].

This builds on `SN|Guru` example by being able to export all items from the
ServiceCatatalog and not just a single item.

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
    python exporter.py --pretty -o dump.json

# Import your dump to another ServiceNow instance

    python importer.py --instance yourinstance2 -i dump.json

# Usage

### Exporter

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
  --catalog=<sys_id>     Specify a catalog to limit --full.  Accepts a CSV.
  --item=<sys_id>        Will export a single catalog item with the matching sys_id.  Accepts a CSV.
  --instance=<instance>  The ServiceNow instance to export from.  Overrides the SNOW_INSTANCE environment variable.
  -o, --output=<file>    Dump the export to a file instead of stdout.
  --pretty               Output JSON pretty formatted.
```

### Importer

```
ServiceNow ServiceCatalog Importer

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
```

# License

[MIT License](LICENSE.txt)

[1]: https://www.servicenowguru.com/system-definition/exporting-service-catalog-items-step/
