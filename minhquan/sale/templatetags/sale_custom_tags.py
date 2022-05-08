import json

from django import template

register = template.Library()

@register.simple_tag
def define(val=None):
  return val

@register.filter
def json_loads(value):
  return json.loads(value)