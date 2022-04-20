from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter()
def to_slugs(list_of_items):
    if list_of_items:
        s = ','.join([item.slug for item in list_of_items])
        return s
    return ''
    