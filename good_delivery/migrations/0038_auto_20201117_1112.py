# Generated by Django 3.1.1 on 2020-11-17 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('good_delivery', '0037_auto_20201117_1111'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gooddelivery',
            name='address_number',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]