# Generated by Django 3.1.1 on 2020-09-21 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('good_delivery', '0013_deliverycampaign_require_user_reservation'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliverycampaign',
            name='new_delivery_if_disabled',
            field=models.BooleanField(default=True),
        ),
    ]
