# Generated by Django 4.0.3 on 2024-04-04 04:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0132_remove_supplierbalancesheet_mrentry_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='supplierbalancesheet',
            name='mr',
        ),
    ]
