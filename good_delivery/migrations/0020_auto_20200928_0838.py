# Generated by Django 3.1.1 on 2020-09-28 06:38

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('good_delivery', '0019_auto_20200925_1549'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliverycampaign',
            name='slug',
            field=models.SlugField(default=1, max_length=255, unique=True, validators=[django.core.validators.RegexValidator(code='invalid_slug', message='Lo slug deve contenere almeno un carattere alfabetico', regex='^(?=.*[a-zA-Z])')]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='deliverycampaign',
            name='name',
            field=models.CharField(help_text='Campagna di consegne', max_length=255, unique=True),
        ),
    ]