# Generated by Django 4.2.5 on 2023-09-15 14:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_alter_product_section'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='store.section'),
        ),
    ]
