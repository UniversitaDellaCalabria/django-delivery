import json
import logging

from django.conf import settings
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from django.templatetags.static import static
from django.utils import timezone
from django.utils.translation import gettext as _
from django.utils.text import slugify

from ckeditor.fields import RichTextField

from . jwts import *


logger = logging.getLogger(__name__)


def _attachment_upload(instance, filename):
    """
    this function has to return the location to upload the file
    """
    folder = instance.get_folder()
    return os.path.join('{}/{}'.format(folder, filename))


class TimeStampedModel(models.Model):
	create = models.DateTimeField(auto_now_add=True)
	modified =  models.DateTimeField(auto_now=True)

	class Meta:
		abstract = True


class DeliveryCampaign(TimeStampedModel):
    """
    bando di consegna beni
    """
    name = models.CharField(max_length=255,
                            help_text=_('Campagna di consegne'),
                            unique=True)
    slug = models.SlugField(max_length=255,
                            blank=False, null=False, unique=True,
                            validators=[
                                RegexValidator(
                                    regex='^(?=.*[a-zA-Z])',
                                    message=_("Lo slug deve contenere "
                                              "almeno un carattere alfabetico"),
                                    code='invalid_slug'
                                ),
                            ])
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    require_agreement = models.BooleanField(default=True)
    identity_document_required = models.BooleanField(default=False)
    operator_can_create = models.BooleanField(default=True)
    new_delivery_if_disabled = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    note_operator = models.TextField(help_text=_('Notes to operators'),
                                     blank=True, null=True)
    note_users = models.TextField(help_text=_('Notes to users'),
                                  blank=True, null=True)
    default_delivered_quantity = models.IntegerField(default=0)

    class Meta:
        verbose_name = _('Campagna di consegne')
        verbose_name_plural = _('Campagne di consegne')

    def is_started(self):
        return self.date_start <= timezone.localtime()

    def is_end(self):
        return self.date_end <= timezone.localtime()

    # @property
    # TODO perchè la data di inizio no?
    def is_in_progress(self):
        return self.is_started() and not self.is_end()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(DeliveryCampaign, self).save(*args, **kwargs)

    def __str__(self):
        return '{}'.format(self.name)


class DeliveryPoint(TimeStampedModel):
    """
    punto di consegna
    """
    campaign = models.ForeignKey(DeliveryCampaign, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, help_text=_('Denominazione'))
    location = models.TextField(max_length=511)
    notes = models.TextField(max_length=511, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Punto di consegna')
        verbose_name_plural = _('Punti di consegna')

    def __str__(self):
        return '({}) {}'.format(self.campaign, self.name)


class OperatorDeliveryPoint(TimeStampedModel):
    """
    operatore di un punto di raccolta
    """
    operator = models.ForeignKey(get_user_model(),
                                 on_delete=models.CASCADE)
    delivery_point = models.ForeignKey(DeliveryPoint,
                                       on_delete=models.CASCADE)
    multi_tenant = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Operatore')
        verbose_name_plural = _('Operatori')

    def __str__(self):
        return '{} - {}'.format(self.operator, self.delivery_point)


class GoodCategory(TimeStampedModel):
    """
    """
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = _('Categoria Bene/Servizio')
        verbose_name_plural = _('Categorie Beni/Servizi')

    def __str__(self):
        return '{}'.format(self.name)


class Good(TimeStampedModel):
    """
    qualsiasi tipo di prodotto da assegnare
    """
    category = models.ForeignKey(GoodCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = _('Bene/Servizio')
        verbose_name_plural = _('Beni/Servizi')

    def __str__(self):
        return '[{}] {}'.format(self.category, self.name)


class DeliveryPointGoodStock(TimeStampedModel):
    delivery_point = models.ForeignKey(DeliveryPoint,
                                       on_delete=models.CASCADE)
    good = models.ForeignKey(Good, on_delete=models.CASCADE)
    max_number = models.IntegerField(default=0,
                                     help_text=_("0 for unlimited"))

    class Meta:
        unique_together = ("good", "delivery_point")
        verbose_name = _('Stock beni centro di consegna')
        verbose_name_plural = _('Stock beni centri di consegna')

    def get_available_items(self):
        delivered_items = GoodDeliveryItem.objects.filter(good_delivery__delivery_point=self.delivery_point,
                                                          good=self.good)

        identifiers = DeliveryPointGoodStockIdentifier.objects.filter(delivery_point_stock=self)
        if identifiers:
            delivered_items = delivered_items.filter(good_stock_identifier__in=identifiers)
            return identifiers.count() - delivered_items.count()

        delivered_quantity = 0
        for delivered_item in delivered_items:
            delivered_quantity += delivered_item.quantity
        if self.max_number > 0:
            return self.max_number - delivered_quantity
        return True

    def __str__(self):
        return '{} - {}'.format(self.delivery_point, self.good)


class DeliveryPointGoodStockIdentifier(TimeStampedModel):
    """
    identificativo bene presente in stock
    """
    delivery_point_stock = models.ForeignKey(DeliveryPointGoodStock,
                                             on_delete=models.CASCADE)
    good_identifier = models.CharField(max_length=255, blank=True, null=True,
                                       help_text=_('Identificativo del prodotto/servizio'))
    notes = models.TextField(max_length=511, null=True, blank=True)

    class Meta:
        verbose_name = _('Identificativo bene in stock')
        verbose_name_plural = _('Identificativi beni in stock')
        unique_together = ("delivery_point_stock", "good_identifier")

    def __str__(self):
        return self.good_identifier


class GoodDelivery(TimeStampedModel):
    """
    assegnazione di un prodotto a un utente, da parte di un operatore
    """
    # autofilled from delivery_point on save()
    campaign = models.ForeignKey(DeliveryCampaign,
                                 on_delete=models.CASCADE)
    choosen_delivery_point = models.ForeignKey(DeliveryPoint,
                                               on_delete=models.PROTECT,
                                               related_name="choosen_delivered_point")
    delivered_to = models.ForeignKey(get_user_model(),
                                     on_delete=models.PROTECT)
    delivery_point = models.ForeignKey(DeliveryPoint,
                                       on_delete=models.PROTECT,
                                       blank=True, null=True,
                                       related_name="delivered_point")
    delivery_date = models.DateTimeField(_('Data di consegna'),
                                         blank=True, null=True)
    delivered_by = models.ForeignKey(get_user_model(),
                                     on_delete=models.PROTECT,
                                     blank=True, null=True,
                                     related_name="delivered_by")
    disabled_point = models.ForeignKey(DeliveryPoint,
                                       on_delete=models.PROTECT,
                                       blank=True, null=True,
                                       related_name="disabled_point")
    disabled_date = models.DateTimeField(_('Data di disabilitazione'),
                                         blank=True, null=True)
    disabled_by = models.ForeignKey(get_user_model(),
                                    on_delete=models.PROTECT,
                                    blank=True, null=True,
                                    related_name="disabled_by")
    disable_notes = models.TextField(null=True, blank=True)
    document_type = models.CharField(max_length=255,
                                     blank=True, null=True)
    document_id = models.CharField(max_length=255, blank=True, null=True)

    address_city = models.CharField(max_length=50, blank=True, null=True)
    address_state = models.CharField(max_length=2, blank=True, null=True)
    address_zip_code = models.CharField(max_length=6, blank=True, null=True)
    address_road = models.CharField(max_length=100, blank=True, null=True)
    address_number = models.CharField(max_length=100, blank=True, null=True)
    address_country = models.CharField(max_length=50, blank=True, null=True)

    phone = models.CharField(max_length=20, blank=True, null=True)

    notes = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = _('Consegna prodotto')
        verbose_name_plural = _('Consegne prodotti')

    def get_stock(self):
        stock = DeliveryPointGoodStock.objects.filter(delivery_point=self.delivery_point,
                                                      good=self.good).first()
        return stock

    def get_items(self):
        items = GoodDeliveryItem.objects.filter(good_delivery=self)
        return items

    def log_action(self, msg, action, user):
        LogEntry.objects.log_action(user_id         = user.pk,
                                    content_type_id = ContentType.objects.get_for_model(self).pk,
                                    object_id       = self.pk,
                                    object_repr     = self.__str__(),
                                    action_flag     = action,
                                    change_message  = msg)
        logger.info(msg)

    def get_year(self):
        return self.create.year

    def build_jwt(self):
        data = {'id': self.pk,
                'user': self.delivered_to.pk,
                'delivery_point': self.delivery_point.pk,
                'modified': self.modified.isoformat()}
        encrypted_data = encrypt_to_jwe(json.dumps(data).encode())
        return encrypted_data

    def is_waiting(self):
        if self.delivery_date: return False
        if self.disabled_date: return False
        return self.get_items()

    def can_be_disabled(self):
        if self.disabled_date: return False
        return True

    def can_be_deleted(self):
        if self.delivery_date: return False
        if self.disabled_date: return False
        user_deliveries = GoodDelivery.objects.filter(campaign=self.campaign,
                                                      delivered_to=self.delivered_to,
                                                      delivery_point=self.delivery_point).count()
        # if good_delivery has been prefilled
        # (not created by operator)
        # operators can't delete it
        if not self.campaign.operator_can_create and user_deliveries==1:
            return False
        return True

    def can_be_marked_by_operator(self):
        # marked as delivered by operator
        # without user confirmation
        if not self.campaign.is_in_progress(): return False
        if self.campaign.require_agreement: return False
        if not self.delivered_by: return False
        return self.is_waiting()

    def can_be_marked_by_user(self):
        """
        marked as delivered by user action
        """
        if not self.delivery_point: return False
        if not self.campaign.is_in_progress(): return False
        if not self.delivered_by: return False
        return self.is_waiting()

    def single_items_to_deliver(self):
        """
        check if there are waiting items that operator has added after
        delivery (for a return)
        """
        if not self.delivery_point: return False
        if not self.campaign.is_in_progress(): return False
        if not self.delivery_date: return False
        waiting_items = GoodDeliveryItem.objects.filter(good_delivery=self,
                                                        create__gt=self.delivery_date,
                                                        return_date__isnull=True,
                                                        delivery_date__isnull=True)
        if waiting_items: return True
        return False

    @property
    def state(self):
        if self.disabled_date:
            return _('disabilitata')
        elif self.delivery_date:
            return _('consegnato')
        elif not self.delivery_point:
            return _('da definire')
        elif self.is_waiting():
            return _('in attesa')
        else:
            return _('unknown')

    def mark_as_delivered(self, delivery_point, operator):
        if not self.delivery_date:
            self.delivery_date = timezone.localtime()
            self.delivered_by = operator
            self.delivery_point = delivery_point
            self.save()
        for item in self.get_items():
            if not item.delivery_date:
                item.delivery_date = timezone.localtime()
            if not item.delivered_by:
                item.delivered_by = operator
            if not item.delivery_point:
                item.delivery_point = delivery_point
            item.save()

    def get_returned_items_to_replace(self):
        returned_good_items = {}
        returned_items = GoodDeliveryItem.objects.filter(good_delivery=self,
                                                         return_date__isnull=False)
        for returned_item in returned_items:
            if returned_good_items.get(returned_item.good):
                returned_good_items[returned_item.good] += 1
            else:
                returned_good_items[returned_item.good] = 1
        for post_delivered in GoodDeliveryItem.objects.filter(good_delivery=self,
                                                              create__gt=self.delivery_date):
            if returned_good_items.get(post_delivered.good):
                returned_good_items[post_delivered.good] -= 1
                if returned_good_items[post_delivered.good] == 0:
                    returned_good_items.pop(post_delivered.good)
        return returned_good_items

    def __str__(self):
        return '{} - {}'.format(self.campaign, self.delivered_to)


class GoodDeliveryItem(TimeStampedModel):
    """
    """
    good_delivery = models.ForeignKey(GoodDelivery,
                                      on_delete=models.CASCADE)
    good = models.ForeignKey(Good, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    good_stock_identifier = models.ForeignKey(DeliveryPointGoodStockIdentifier,
                                              blank=True, null=True,
                                              on_delete=models.CASCADE)
    good_identifier = models.CharField(max_length=255, blank=True, null=True)
    delivery_point = models.ForeignKey(DeliveryPoint,
                                       on_delete=models.PROTECT,
                                       blank=True, null=True,
                                       related_name="item_delivered_point")
    delivery_date = models.DateTimeField(_('Data di consegna'),
                                         blank=True, null=True)
    delivered_by = models.ForeignKey(get_user_model(),
                                     on_delete=models.PROTECT,
                                     blank=True, null=True,
                                     related_name="item_delivered_by")
    returned_point = models.ForeignKey(DeliveryPoint,
                                       on_delete=models.PROTECT,
                                       blank=True, null=True,
                                       related_name="returned_point")
    return_date = models.DateTimeField(_('Data di restituzione'),
                                       blank=True, null=True)
    returned_to = models.ForeignKey(get_user_model(),
                                    on_delete=models.PROTECT,
                                    blank=True, null=True,
                                    related_name="returned_to")

    class Meta:
        verbose_name = _('Oggetto consegnato')
        verbose_name_plural = _('Oggetti consegnati')

    def can_be_returned(self):
        if not self.good_delivery.delivery_date: return False
        if not self.delivery_date: return False
        if not self.good_identifier: return False
        if self.return_date: return False
        return True

    def can_be_deleted(self):
        if self.delivery_date: return False
        if self.return_date: return False
        return True

    def __str__(self):
        return '{}'.format(self.good)


class Agreement(TimeStampedModel):
    """
    accettazione condizioni
    """
    name = models.CharField(max_length=255)
    # description = models.TextField(max_length=1023)
    subject = models.CharField(max_length=255)
    description = RichTextField(max_length=12000)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Agreement')
        verbose_name_plural = _('Agreements')

    def __str__(self):
        return '{}'.format(self.name)


class DeliveryCampaignAgreement(TimeStampedModel):
    """
    agreement associato a una consegna
    """
    campaign = models.ForeignKey(DeliveryCampaign,
                                 on_delete=models.PROTECT)
    agreement = models.ForeignKey(Agreement, on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Agreement consegna')
        verbose_name_plural = _('Agreement consegne')

    def __str__(self):
        return '{} - {}'.format(self.campaign, self.agreement)


class GoodDeliveryAttachment(TimeStampedModel):
    """
    documenti allegati a consegna bene
    """
    good_delivery = models.ForeignKey(GoodDelivery,
                                      on_delete=models.PROTECT)
    attachment = models.FileField(upload_to=_attachment_upload,
                                  null=True, blank=True,
                                  max_length=255)

    class Meta:
        verbose_name = _('Allegato consegna bene')
        verbose_name_plural = _('Allegati consegne beni')

    def get_folder(self):
        """
        returns GoodDelivery attachments folder
        """
        folder = '{}/{}/{}'.format('good_deliveries',
                                   self.good_delivery.get_year(),
                                   self.good_delivery.pk)
        return folder

    def __str__(self):
        return '{} - {}'.format(self.good_delivery, self.attachment)
