# Generated by Django 3.1.1 on 2020-10-06 08:37

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('good_delivery', '0034_agreement_subject'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agreement',
            name='description',
            field=ckeditor.fields.RichTextField(max_length=12000),
        ),
    ]
