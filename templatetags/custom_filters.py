from django import template

register = template.Library()

@register.filter
def split_by_comma(value):
    """Split a string by comma and return list"""
    if not value:
        return []
    return [item.strip() for item in value.split(',')]

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    return dictionary.get(key, [])