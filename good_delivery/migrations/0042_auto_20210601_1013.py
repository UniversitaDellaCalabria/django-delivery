# Generated by Django 3.1.1 on 2021-06-01 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('good_delivery', '0041_auto_20210601_1009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gooddeliveryitem',
            name='quantity',
            field=models.PositiveIntegerField(),
        ),
    ]
