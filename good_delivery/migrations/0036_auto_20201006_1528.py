# Generated by Django 3.1.1 on 2020-10-06 13:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('good_delivery', '0035_auto_20201006_1037'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='deliverypointgoodstockidentifier',
            unique_together={('delivery_point_stock', 'good_identifier')},
        ),
    ]
