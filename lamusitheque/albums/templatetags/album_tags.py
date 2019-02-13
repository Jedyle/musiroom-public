from django import template

register = template.Library()

@register.filter(is_safe=True)
def is_numeric(value):
    return "{}".format(value).isdigit()

@register.filter(name='subtract')
def subtract(value, arg):
    return int(value) -int(arg)
