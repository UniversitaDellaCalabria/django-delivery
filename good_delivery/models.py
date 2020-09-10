from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _


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

    class Meta:
        verbose_name = _('Campagna di consegne')
        verbose_name_plural = _('Campagne di consegne')

    @property
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

    class Meta:
        verbose_name = _('Utenteal punto di raccolta')
        verbose_name_plural = _('Utenti ai punti di raccolta')
        unique_together = ("user", "delivery_point")

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
    # 0 for unlimited
    max_number = models.IntegerField(default=0)

    class Meta:
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
        verbose_name = _('Idenficativo bene in stock')
        verbose_name_plural = _('Idenficativi beni in stock')

    def __str__(self):
        return '{} - {}'.format(self.delivery_point_stock,
                                self.good_identifier)


class GoodDelivery(TimeStampedModel):
    """
    assegnazione di un prodotto a un utente, da parte di un operatore
    """
    delivered_to = models.ForeignKey(get_user_model(),
                                     on_delete=models.PROTECT)
    delivered_by = models.ForeignKey(OperatorDeliveryPoint,
                                     on_delete=models.PROTECT)
    good = models.ForeignKey(Good, on_delete=models.PROTECT)
    good_stock_identifier = models.ForeignKey(DeliveryPointGoodStockIdentifier,
                                              blank=True, null=True,
                                              on_delete=models.PROTECT)
    # se non è presente un identificativo in stock
    # ma l'operatore deve specificarlo
    good_identifier = models.CharField(max_length=255, blank=True, null=True)
    delivery_date = models.DateTimeField(_('Data di consegna'),
                                         blank=True, null=True)
    disabled_date = models.DateTimeField(_('Data di disabilitazione'),
                                         blank=True, null=True)
    return_date = models.DateTimeField(_('Data di restituzione'),
                                       blank=True, null=True)
    notes = models.TextField(max_length=1023, null=True, blank=True)

    class Meta:
        verbose_name = _('Consegna prodotto')
        verbose_name_plural = _('Consegne prodotti')

    def get_year(self):
        return self.delivery_date.year

    def __str__(self):
        return '{} - {}'.format(self.user, self.product)

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
    description = models.TextField(max_length=1023)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Agreement')
        verbose_name_plural = _('Agreements')

    def __str__(self):
        return '{}'.format(self.name)


class GoodDeliveryAgreement(TimeStampedModel):
    """
    agreement associato a una consegna
    """
    good_delivery = models.ForeignKey(GoodDelivery,
                                      on_delete=models.PROTECT)
    agreement = models.ForeignKey(Agreement, on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Agreement consegna')
        verbose_name_plural = _('Agreement consegne')

    def __str__(self):
        return '{} - {}'.format(self.good_delivery, self.agreement)


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
