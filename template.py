from jinja2 import Template
import json
import re


def get_value_by_type(obj):
    value = str(obj)
    if isinstance(obj, bool):
        value.lower()
    if re.match(r'.*[<>].*', value):
        return '<![CDATA[%s]]>' % value
    else:
        return value

def is_dict(obj):
    isinstance(obj, dict)

template = """
{% macro format_value(value) -%}
    {%- if value is mapping -%}
        {{value['value']}}
    {%- elif '<' in value or '>' in value -%}
        <![CDATA[{{value}}]]>
    {%- else -%}
        {{value | escape}}
    {%- endif -%}
{%- endmacro %}
<?xml version="1.0" encoding="UTF-8"?>
<unload>{%- for table in tables %}
   {%- for record in tables[table] %}
   <{{table}} action="INSERT_OR_UPDATE">
   {%- for field, value in record | dictsort %}
   {%- if format_value(value) %}
      <{{field}}>{{format_value(value)}}</{{field}}>
   {%- else %}
      <{{field}} />
   {%- endif %}
   {%- endfor %}
   </{{table}}>
   {%- endfor %}
{%- endfor %}
</unload>
""".strip()
"""
"""

export = {}
with open('dump.json') as f:
    export = json.load(f)

t = Template(template)
print t.render(tables = export).strip()
