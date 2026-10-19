from django import template

register = template.Library()


@register.filter
def trim_start(value):
    if value is None:
        return ""
    return str(value).lstrip()
