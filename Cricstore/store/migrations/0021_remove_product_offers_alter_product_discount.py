# Generated by Django 4.2.5 on 2023-10-19 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0020_offer_category_offers_product_offers'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='offers',
        ),
        migrations.AlterField(
            model_name='product',
            name='discount',
            field=models.IntegerField(blank=True),
        ),
    ]
