# {{ obj_dict["class"] }}

## Params
{% for param_desc in obj_dict["params"] %}
{{ param_desc | safe}}
{% endfor %}

## Backwards links
{% for linked_obj in obj_dict["modeling_obj_containers"] %}
- [{{ linked_obj }}]({{ linked_obj }}.md)
{% endfor %}

## Calculated attributes
{% for calculated_attr_desc in obj_dict["calculated_attrs"] %}
{{ calculated_attr_desc | safe}}
{% endfor %}