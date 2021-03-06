# Generated by Django 3.1.1 on 2020-09-11 08:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import good_delivery.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Agreement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(max_length=1023)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Agreement',
                'verbose_name_plural': 'Agreements',
            },
        ),
        migrations.CreateModel(
            name='DeliveryCampaign',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(help_text='Campagna di consegne', max_length=255)),
                ('date_start', models.DateTimeField()),
                ('date_end', models.DateTimeField()),
                ('require_agreement', models.BooleanField(default=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Campagna di consegne',
                'verbose_name_plural': 'Campagne di consegne',
            },
        ),
        migrations.CreateModel(
            name='DeliveryPoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(help_text='Denominazione', max_length=255)),
                ('location', models.TextField(max_length=511)),
                ('notes', models.TextField(blank=True, max_length=511, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='good_delivery.deliverycampaign')),
            ],
            options={
                'verbose_name': 'Punto di consegna',
                'verbose_name_plural': 'Punti di consegna',
            },
        ),
        migrations.CreateModel(
            name='DeliveryPointGoodStock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('max_number', models.IntegerField(default=0)),
                ('delivery_point', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='good_delivery.deliverypoint')),
            ],
            options={
                'verbose_name': 'Stock beni centro di consegna',
                'verbose_name_plural': 'Stock beni centri di consegna',
            },
        ),
        migrations.CreateModel(
            name='DeliveryPointGoodStockIdentifier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('good_identifier', models.CharField(blank=True, help_text='Identificativo del prodotto/servizio', max_length=255, null=True)),
                ('delivery_point_stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='good_delivery.deliverypointgoodstock')),
            ],
            options={
                'verbose_name': 'Idenficativo bene in stock',
                'verbose_name_plural': 'Idenficativi beni in stock',
            },
        ),
        migrations.CreateModel(
            name='Good',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Bene/Servizio',
                'verbose_name_plural': 'Beni/Servizi',
            },
        ),
        migrations.CreateModel(
            name='GoodCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'verbose_name': 'Categoria Bene/Servizio',
                'verbose_name_plural': 'Categorie Beni/Servizi',
            },
        ),
        migrations.CreateModel(
            name='GoodDelivery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('good_identifier', models.CharField(blank=True, max_length=255, null=True)),
                ('delivery_date', models.DateTimeField(blank=True, null=True, verbose_name='Data di consegna')),
                ('disabled_date', models.DateTimeField(blank=True, null=True, verbose_name='Data di disabilitazione')),
                ('return_date', models.DateTimeField(blank=True, null=True, verbose_name='Data di restituzione')),
                ('notes', models.TextField(blank=True, max_length=1023, null=True)),
            ],
            options={
                'verbose_name': 'Consegna prodotto',
                'verbose_name_plural': 'Consegne prodotti',
            },
        ),
        migrations.CreateModel(
            name='OperatorDeliveryPoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('delivery_point', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='good_delivery.deliverypoint')),
                ('operator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Operatore',
                'verbose_name_plural': 'Operatori',
            },
        ),
        migrations.CreateModel(
            name='GoodDeliveryAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('attachment', models.FileField(blank=True, max_length=255, null=True, upload_to=good_delivery.models._attachment_upload)),
                ('good_delivery', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='good_delivery.gooddelivery')),
            ],
            options={
                'verbose_name': 'Allegato consegna bene',
                'verbose_name_plural': 'Allegati consegne beni',
            },
        ),
        migrations.CreateModel(
            name='GoodDeliveryAgreement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('agreement', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='good_delivery.agreement')),
                ('good_delivery', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='good_delivery.gooddelivery')),
            ],
            options={
                'verbose_name': 'Agreement consegna',
                'verbose_name_plural': 'Agreement consegne',
            },
        ),
        migrations.AddField(
            model_name='gooddelivery',
            name='delivered_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='good_delivery.operatordeliverypoint'),
        ),
        migrations.AddField(
            model_name='gooddelivery',
            name='delivered_to',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='gooddelivery',
            name='good',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='good_delivery.good'),
        ),
        migrations.AddField(
            model_name='gooddelivery',
            name='good_stock_identifier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='good_delivery.deliverypointgoodstockidentifier'),
        ),
        migrations.AddField(
            model_name='good',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='good_delivery.goodcategory'),
        ),
        migrations.AddField(
            model_name='deliverypointgoodstock',
            name='good',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='good_delivery.good'),
        ),
        migrations.CreateModel(
            name='UserDeliveryPoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('delivery_point', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='good_delivery.deliverypoint')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Utenteal punto di raccolta',
                'verbose_name_plural': 'Utenti ai punti di raccolta',
                'unique_together': {('user', 'delivery_point')},
            },
        ),
    ]
