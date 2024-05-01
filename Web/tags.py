from django import template

register = template.Library()

@register.simple_tag
def is_chose(value):
    return True