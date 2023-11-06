from django import template

register = template.Library()

@register.filter
def calculate_order_total(cart_total_amount, tax, discount, delivery_charge):
    total = cart_total_amount + tax - discount + delivery_charge
    return total

