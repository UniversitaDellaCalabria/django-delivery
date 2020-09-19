import json
import logging

from django.conf import settings
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.templatetags.static import static
from django.utils import timezone
from django.utils.translation import gettext as _

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
                            help_text=_('Campagna di consegne'))
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    require_agreement = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    
    note_operator = models.TextField(help_text=_('Notes to operators'),
                                     blank=True, null=True)
    note_users = models.TextField(help_text=_('Notes to users'),
                                     blank=True, null=True)
    
    class Meta:
        verbose_name = _('Campagna di consegne')
        verbose_name_plural = _('Campagne di consegne')

    # @property
    def is_in_progress(self):
        return self.date_start<=timezone.now() and self.date_end>timezone.now()

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


class UserDeliveryPoint(TimeStampedModel):
    """
    assegnazione utenti finali a un punto di raccolta
    """
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    delivery_point = models.ForeignKey(DeliveryPoint, on_delete=models.CASCADE)
    
    @property
    def state(self):
        delivery = GoodDelivery.objects.filter(delivered_to=self.user,
                                               campaign=self.delivery_point.campaign).last()
        if delivery:
            return delivery.state
        else:
            return _('da consegnare')
            
        
    
    class Meta:
        verbose_name = _('Prenotazioni utenti')
        verbose_name_plural = _('Prenotazioni utenti')
        unique_together = ("user", "delivery_point")


    def get_good_deliveries(self):
        deliveries = GoodDelivery.objects.filter(delivered_to=self.user,
                                                 created_by__delivery_point=self.delivery_point).count()
        return deliveries

    def __str__(self):
        return '{} - {}'.format(self.user, self.delivery_point)

    #onsave
    #same user can't join multiple delivery point in a campaign


class OperatorDeliveryPoint(TimeStampedModel):
    """
    operatore di un punto di raccolta
    """
    operator = models.ForeignKey(get_user_model(),
                                 on_delete=models.CASCADE)
    delivery_point = models.ForeignKey(DeliveryPoint,
                                       on_delete=models.CASCADE)
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
        return '{} - {}'.format(self.category, self.name)


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

    class Meta:
        verbose_name = _('Identificativo bene in stock')
        verbose_name_plural = _('Identificativi beni in stock')

    def __str__(self):
        return '{} - {}'.format(self.delivery_point_stock,
                                self.good_identifier)


class GoodDelivery(TimeStampedModel):
    """
    assegnazione di un prodotto a un utente, da parte di un operatore
    """
    campaign = models.ForeignKey(DeliveryCampaign,
                                 on_delete=models.CASCADE)
    delivered_to = models.ForeignKey(get_user_model(),
                                     on_delete=models.CASCADE)
    created_by = models.ForeignKey(OperatorDeliveryPoint,
                                   on_delete=models.CASCADE,
                                   related_name="created_by")
    good = models.ForeignKey(Good, on_delete=models.CASCADE)
    good_stock_identifier = models.ForeignKey(DeliveryPointGoodStockIdentifier,
                                              blank=True, null=True,
                                              on_delete=models.CASCADE)
    # se non è presente un identificativo in stock
    # ma l'operatore deve specificarlo
    good_identifier = models.CharField(max_length=255, blank=True, null=True)
    delivery_date = models.DateTimeField(_('Data di consegna'),
                                         blank=True, null=True)
    delivered_by = models.ForeignKey(OperatorDeliveryPoint,
                                     on_delete=models.CASCADE,
                                     blank=True, null=True,
                                     related_name="deliveder_by")
    disabled_date = models.DateTimeField(_('Data di disabilitazione'),
                                         blank=True, null=True)
    disabled_by = models.ForeignKey(OperatorDeliveryPoint,
                                    on_delete=models.CASCADE,
                                    blank=True, null=True,
                                    related_name="disabled_by")
    return_date = models.DateTimeField(_('Data di restituzione'),
                                       blank=True, null=True)
    returned_to = models.ForeignKey(OperatorDeliveryPoint,
                                    on_delete=models.CASCADE,
                                    blank=True, null=True,
                                    related_name="returned_to")
    notes = models.TextField(max_length=1023, null=True, blank=True)

    class Meta:
        verbose_name = _('Consegna prodotto')
        verbose_name_plural = _('Consegne prodotti')

    def save(self, *args, **kwargs):
        # good identifiers
        stock_identifier = self.good_stock_identifier
        manual_identifier = self.good_identifier

        # only one identifier is permitted
        if stock_identifier and manual_identifier:
            raise Exception(_("Al più un identificatore"))

        delivery_point = self.created_by.delivery_point
        good = self.good
        stock = DeliveryPointGoodStock.objects.filter(delivery_point=delivery_point,
                                                      good=good).first()
        stock_identifiers = DeliveryPointGoodStockIdentifier.objects.filter(delivery_point_stock=stock)

        # if a stock identifiers list is available,
        # manual identifier is not permitted
        if stock_identifiers and not self.good_stock_identifier:
            raise Exception(_("Selezionare il codice identificativo "
                              "dalla lista"))

        campaign = delivery_point.campaign
        # check if there is an existent delivery
        # (same good, same id, same campaign)
        existent_delivery = GoodDelivery.objects.filter(Q(good_stock_identifier=stock_identifier) &
                                                        Q(good_stock_identifier__isnull=False) |
                                                        Q(good_identifier=manual_identifier) &
                                                        Q(good_identifier__isnull=False),
                                                        good=good,
                                                        created_by__delivery_point__campaign=campaign)
                                                        # return_date__isnull=True)
        # if operator is editing a delivery (self.pk exists)
        # we can exclude it from deliveries list
        if self.pk:
            existent_delivery = existent_delivery.exclude(pk=self.pk)
        existent_delivery = existent_delivery.first()
        # if there is a delivery with same good code
        # (same good, same id, same campaign)
        # save operation is not permitted!
        if existent_delivery:
            raise Exception(_("Esiste già una consegna di questo prodotto, "
                              "per questa campagna, "
                              "con questo codice identificativo"))

        super(GoodDelivery, self).save(*args, **kwargs)

    def log_action(self, msg, action, user):
        LogEntry.objects.log_action(user_id         = user.pk,
                                    content_type_id = ContentType.objects.get_for_model(self).pk,
                                    object_id       = self.pk,
                                    object_repr     = self.__str__(),
                                    action_flag     = action,
                                    change_message  = msg)
        logger.info(msg)

    def get_year(self):
        return self.delivery_date.year

    def build_jwt(self):
        data = {'id': self.pk,
                'user': self.delivered_to.pk}
        # serialized = serializers.serialize('json', [good_delivery], ensure_ascii=False)
        encrypted_data = encrypt_to_jwe(json.dumps(data).encode())
        return encrypted_data
        # decrypted = json.loads(decrypt_from_jwe(encrypted_data))
        # return decrypted

    def is_waiting(self):
        if self.delivery_date: return False
        if self.return_date: return False
        if self.disabled_date: return False
        return True
    
    @property
    def state(self):
        if self.is_waiting():
            return _('waiting')
        elif self.disabled_date:
            return _('disabled')
        elif self.delivery_date:
            return _('delivered')
        else:
            return _('unknown')

    def __str__(self):
        return '{} - {}'.format(self.delivered_to, self.good)

    # TODO save()

    # gestione errori di consegna prodotti (codici errati)
    # ----------------------------------------------------
    # se returned=True allora il prodotto è stato riconsegnato
    # non è possibile assegnare lo stesso codice a più utenti,
    # a me no che questo non sia stato riconsegnato

    # check relazioni user e product con DeliveryPoint
    # ----------------------------------------------
    # per verificare la consistenza dei dati e l'effettiva
    # corrispondenza e validità dell'operazione


class Agreement(TimeStampedModel):
    """
    accettazione condizioni
    """
    name = models.CharField(max_length=255)
    # description = models.TextField(max_length=1023)
    description = RichTextField(max_length=1023)
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
