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
    {% if '<' in value or '>' in value
        %}<![CDATA[{{value}}]]>{%
    else
        %}{{value}}{% endif %}
{%- endmacro %}
<?xml version="1.0" encoding="UTF-8"?>
<unload>
    {%- for table in tables %}
    <{{table}} action="INSERT_OR_UPDATE">
    {%- for record in tables[table] -%} {%- for field, value in record.items() recursive %} {%- if value is mapping %}
        <{{field}}>{{loop(value.items()) | indent(4, True)}}
        </{{field}}>
    {%- elif value %}
        <{{field}}>{{format_value(value)}}</{{field}}>
    {%- else %}
        <{{field}} />
    {%- endif %} {%- endfor -%} {%- endfor %}
    </{{table}}>
{% endfor %}</unload>
""".strip()
"""
"""

export = {}
with open('dump.json') as f:
    export = json.load(f)

t = Template(template)
print t.render(processor=get_value_by_type, tables = export)
