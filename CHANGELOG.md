# release 0.3

New utility:

- Now there's an `importer.py` to import the JSON dump from `exporter.py`.

New features:

- New option `exporter.py --pretty` which, when enabled, outputs JSON pretty
  formatted.

# release 0.2

New features:

- Limit full dump to one or more catalogs.  New option `--catalog` can be passed
  a single catalog `sys_id` or a comma separated value list of catalog `sys_id`.
- Limit item dump to one or more items.  `--item` option now supports a comma
  separated value list of item `sys_id` in addition to just a single `sys_id`.

# First release version 0.1

Commandline option support.

- Export a single ServiceCatalog catalog item.
- Export all ServiceCatalog catalog items.

Export service catalog items.

- Variables (including question choices)
- Variable sets (including associated variables, client scripts, and UI
  policies)
- Client scripts
- UI policies
- Additional categories
- Approved by user and group
- Available for/Not Available for lists
- Order guide rule base

Based on an original solution by [SN|Guru][snguru].

[snguru]: https://www.servicenowguru.com/system-definition/exporting-service-catalog-items-step/
