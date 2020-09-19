# Generated by Django 3.1.1 on 2020-09-19 15:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('good_delivery', '0008_auto_20200919_1700'),
    ]

    operations = [
        migrations.AddField(
            model_name='gooddelivery',
            name='campaign',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='good_delivery.deliverycampaign'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='gooddelivery',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_by', to='good_delivery.operatordeliverypoint'),
        ),
        migrations.AlterField(
            model_name='gooddelivery',
            name='delivered_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='deliveder_by', to='good_delivery.operatordeliverypoint'),
        ),
        migrations.AlterField(
            model_name='gooddelivery',
            name='delivered_to',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='gooddelivery',
            name='disabled_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='disabled_by', to='good_delivery.operatordeliverypoint'),
        ),
        migrations.AlterField(
            model_name='gooddelivery',
            name='good',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='good_delivery.good'),
        ),
        migrations.AlterField(
            model_name='gooddelivery',
            name='good_stock_identifier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='good_delivery.deliverypointgoodstockidentifier'),
        ),
        migrations.AlterField(
            model_name='gooddelivery',
            name='returned_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='returned_to', to='good_delivery.operatordeliverypoint'),
        ),
    ]
