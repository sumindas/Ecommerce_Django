from django.apps import AppConfig
from django import template


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'
    def ready(self):
        from store import custom_filters
        library = template.Library()
        library.filter('calculate_stock', custom_filters.calculate_stock)