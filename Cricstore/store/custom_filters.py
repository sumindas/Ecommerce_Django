# custom_filters.py
from django import template

register = template.Library()

@register.filter(name='calculate_stock')
def calculate_stock(product):
    return product.total_quantity - product.availability
