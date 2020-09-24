import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from . forms import *
from . models import *
from . templatetags.good_delivery_tags import (current_date,
                                               markdown,
                                               user_from_pk)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

_user_admin = dict(username='admin', password='admin',
                   is_superuser=1, is_staff=1)
_user_op = dict(username='ciro', email='thatmail@ingoalla.org')
_user = dict(username='utonto', email='thatmail@utonti.org')

campaign_data = dict(name='banane',
                     date_start=timezone.localtime(),
                     date_end=timezone.localtime() + timezone.timedelta(hours=3),
                     is_active=True,
                     require_agreement=True,
                     new_delivery_if_disabled=True)


class GoodDeliveryTest(TestCase):

    def setUp(self):
        self.admin = get_user_model().objects.create(**_user_admin)
        self.user = get_user_model().objects.create(**_user)
        self.operator = get_user_model().objects.create(**_user_op)
        self.client = Client(enforce_csrf_checks=True)

        self.good_cat_food = GoodCategory.objects.create(name='food')
        self.good_cat_gear = GoodCategory.objects.create(name='hitech')
        self.good_food = Good.objects.create(name='banana', category=self.good_cat_food)
        self.good_gear = Good.objects.create(name='sim/router', category=self.good_cat_gear)


    def _campaign_food(self):
        data = campaign_data.copy()
        data['operator_can_create'] = True
        campaign = DeliveryCampaign.objects.create(**data)
        devpoint = DeliveryPoint.objects.create(campaign=campaign,
                                                name='ufficio_frutta')
        op_devpoint = OperatorDeliveryPoint.objects.create(delivery_point=devpoint,
                                                           operator=self.operator)
        good_devpoint = DeliveryPointGoodStock.objects.create(delivery_point=devpoint,
                                                              good=self.good_food,
                                                              max_number=0)
        return op_devpoint, good_devpoint


    def _campaign_gear(self):
        data = campaign_data.copy()
        data['name'] = 'gears'
        data['operator_can_create'] = False
        campaign = DeliveryCampaign.objects.create(**data)
        devpoint = DeliveryPoint.objects.create(campaign=campaign,
                                                name='ufficio_gear')

        op_devpoint = OperatorDeliveryPoint.objects.create(delivery_point=devpoint,
                                                           operator=self.operator)
        good_devpoint_stock = DeliveryPointGoodStock.objects.create(delivery_point=devpoint,
                                                              good=self.good_gear,
                                                              max_number=0)
        booking = GoodDelivery.objects.create(delivery_point=devpoint,
                                              delivered_to=self.user,
                                              good=self.good_gear)
        return booking, good_devpoint_stock


    def test_op_gear(self):
        self.client.force_login(self.operator)

        url = reverse('good_delivery:operator_active_campaigns')
        home = self.client.get(url)
        assert b'non abilitato' in home.content

        campaign_booking, good_devpoint_stock = self._campaign_gear()
        url = reverse('good_delivery:operator_active_campaigns')
        home = self.client.get(url, follow=True)
        assert b'Prenotazioni da gestire' in home.content

    def _get_csrfmiddlewaretoken(self, context):
        """
        context = self.client.get().context
        returns a POSTable data dict
        """
        csrfmiddlewaretoken = context.get('csrf_token').__str__()
        return {'csrfmiddlewaretoken': csrfmiddlewaretoken}

    def test_op_create_delivery(self):
        """
        cannot do that, only booked delivery allowed
        """
        self.client.force_login(self.operator)
        campaign_booking, good_devpoint_stock = self._campaign_gear()

        url_kwargs = dict(campaign_id=good_devpoint_stock.delivery_point.campaign.pk,
                          user_id=self.user.pk,
                          good_stock_id=good_devpoint_stock.pk)
        url = reverse('good_delivery:operator_new_delivery',
                      kwargs=url_kwargs)
        req = self.client.get(url)

        assert req.status_code == 403


    def test_op_create_delivery_food(self):
        """
        delivery without booking
        """
        self.client.force_login(self.operator)
        op_devpoint, good_devpoint_stock = self._campaign_food()

        url_kwargs = dict(campaign_id=op_devpoint.delivery_point.campaign.pk,
                          user_id=self.user.pk,
                          good_stock_id=good_devpoint_stock.pk)
        url = reverse('good_delivery:operator_new_delivery',
                      kwargs=url_kwargs)
        req = self.client.get(url, follow=True)

        # POST
        csrf_data = self._get_csrfmiddlewaretoken(req.context)
        # first try, failed csrf
        data = {'quantity': 1}
        data.update(csrf_data)
        req = self.client.post(url, data=data, follow=True)

        assert b'Inserimento effettuato' in req.content
        assert req.status_code == 200


    def _get_operator_good_delivery_detail(self):
        self.client.force_login(self.operator)
        campaign_booking, good_devpoint_stock = self._campaign_gear()
        url_kwargs = dict(campaign_id=good_devpoint_stock.delivery_point.campaign.pk,
                          delivery_id=campaign_booking.pk)
        url = reverse('good_delivery:operator_good_delivery_detail',
                       kwargs=url_kwargs)
        return url, campaign_booking, good_devpoint_stock


    def test_op_update_booked_delivery(self):
        url, campaign_booking, good_devpoint_stock = \
            self._get_operator_good_delivery_detail()
        req = self.client.get(url, follow=True)
        assert req.status_code == 200
        assert b'Attesa ritiro' in req.content

        # test form
        data = {'quantity': 1}
        form = GoodDeliveryForm(data=data, stock=good_devpoint_stock)
        assert form.is_valid()

        csrf_data = self._get_csrfmiddlewaretoken(req.context)
        data.update(csrf_data)
        # first try, failed csrf - MUST FAIL
        # WARNING:django.security.csrf:Forbidden (CSRF token missing or incorrect.)
        req = self.client.post(url, data={})
        assert req.status_code == 403

        req = self.client.post(url, data=data, follow=True)
        assert b'Modifica effettuata correttamente' in req.content

        url_kwargs = dict(campaign_id=good_devpoint_stock.delivery_point.campaign.pk,
                  delivery_id=campaign_booking.pk)
        url = reverse('good_delivery:operator_good_delivery_send_token',
              kwargs=url_kwargs)
        req = self.client.get(url, follow=True)
        assert b'Link di attivazione inviato' in req.content

        gd = GoodDelivery.objects.get(pk=campaign_booking.pk)
        assert gd.state == 'in attesa'


        # user access
        self.client.force_login(self.user)

        url = reverse('good_delivery:user_index')
        home = self.client.get(url)
        assert b'In corso' in home.content


    def test_op_delivery_campaign_expired(self):
        url, campaign_booking, good_devpoint_stock = \
            self._get_operator_good_delivery_detail()

        req = self.client.get(url)
        csrf_data = self._get_csrfmiddlewaretoken(req.context)

        # test campaign not in progress
        campaign_booking.campaign.date_end = timezone.localtime() - \
                                             timezone.timedelta(days=1024)
        campaign_booking.campaign.save()
        assert not campaign_booking.campaign.is_in_progress()

        req = self.client.post(url, data=csrf_data, follow=True)
        assert b'Campagna non in corso' in req.content


    def test_op_delivery_not_waiting(self):
        url, campaign_booking, good_devpoint_stock = \
            self._get_operator_good_delivery_detail()

        req = self.client.get(url)
        csrf_data = self._get_csrfmiddlewaretoken(req.context)

        campaign_booking.disabled_date = timezone.localtime()
        campaign_booking.save()
        assert not campaign_booking.is_waiting()
        req = self.client.post(url, data=csrf_data, follow=True)
        assert b'La consegna non' in req.content


    def test_op_delivery_disable(self):
        _, campaign_booking, good_devpoint_stock = \
            self._get_operator_good_delivery_detail()
        url_kwargs = dict(campaign_id=campaign_booking.campaign.pk,
                          delivery_id=campaign_booking.pk)
        url = reverse('good_delivery:operator_good_delivery_disable',
                      kwargs=url_kwargs)

        req = self.client.get(url, follow=True)
        gd = GoodDelivery.objects.get(pk=campaign_booking.pk)
        assert gd.disabled_date
        assert gd.state == 'disabilitata'
        assert b'Disabilitazione completata' in req.content

        url = reverse('good_delivery:operator_good_delivery_send_token',
                      kwargs=url_kwargs)
        req = self.client.get(url, follow=True)
        assert b'Consegna bloccata' in req.content


    def test_op_delivery_delete(self):
        _, campaign_booking, good_devpoint_stock = \
            self._get_operator_good_delivery_detail()
        url_kwargs = dict(campaign_id=campaign_booking.campaign.pk,
                          delivery_id=campaign_booking.pk)
        url = reverse('good_delivery:operator_good_delivery_delete',
                      kwargs=url_kwargs)

        req = self.client.get(url, follow=True)
        assert not GoodDelivery.objects.filter(pk=campaign_booking.pk)
        assert b'consegna eliminata' in req.content

        url = reverse('good_delivery:operator_good_delivery_send_token',
                      kwargs=url_kwargs)
        req = self.client.get(url, follow=True)
        assert req.status_code == 404

    def test_op_delivery_preload(self):
        """
        if booking required will be not available
        """
        _, campaign_booking, good_devpoint_stock = \
            self._get_operator_good_delivery_detail()
        url_kwargs = dict(campaign_id=campaign_booking.campaign.pk)
        url = reverse('good_delivery:operator_new_delivery_preload',
                      kwargs=url_kwargs)
        req = self.client.get(url, follow=True)
        assert req.status_code == 403

        campaign_booking.campaign.operator_can_create = True
        campaign_booking.campaign.save()
        req = self.client.get(url, follow=True)
        assert b'Nuova consegna' in req.content

        csrf_data = self._get_csrfmiddlewaretoken(req.context)
        # first try, failed csrf
        data = dict()
        data.update(csrf_data)
        data['good_stock'] = 1
        data['user'] = 2
        req = self.client.post(url, data=data, follow=True)
        assert b'inserito con successo' in req.content


    def test_good_delivery_tags(self):
        logger.info('test tags')        
        logger.info(current_date())
        logger.info(markdown('*hello*\n- a\n- b'))
        logger.info(user_from_pk(1))


    def test_good_delivery_attachment(self):
        campaign_booking, good_devpoint_stock = self._campaign_gear()
        gda = GoodDeliveryAttachment.objects.create(good_delivery=campaign_booking)
        gda.get_folder()


    def test_operator_another_delivery(self):
        _, campaign_booking, good_devpoint_stock = \
            self._get_operator_good_delivery_detail()
        url_kwargs = dict(campaign_id=campaign_booking.campaign.pk,
                          good_delivery_id=campaign_booking.pk)
        url = reverse('good_delivery:operator_another_delivery',
                      kwargs=url_kwargs)
        req = self.client.get(url, follow=True)
        assert b'Processi di consegna attivi' in req.content
        
        # disable
        gd = GoodDelivery.objects.get(pk=campaign_booking.pk)
        gd.disabled_date = timezone.localtime()
        gd.save()
        
        req = self.client.get(url, follow=True)
        # POST
        csrf_data = self._get_csrfmiddlewaretoken(req.context)
        # first try, failed csrf
        data = {'quantity': 1}
        data.update(csrf_data)
        req = self.client.post(url, data=data, follow=True)

        assert b'Inserimento effettuato' in req.content
        assert req.status_code == 200


    def test_operator_good_delivery_return(self):
        _, campaign_booking, good_devpoint_stock = \
            self._get_operator_good_delivery_detail()
        url_kwargs = dict(campaign_id=campaign_booking.campaign.pk,
                          delivery_id=campaign_booking.pk)
        url = reverse('good_delivery:operator_good_delivery_return',
                      kwargs=url_kwargs)
        
        # this covers the check
        req = self.client.get(url, follow=True)
        assert b'Consegna non ancora effettuata' in req.content
        
        gd = GoodDelivery.objects.get(pk=campaign_booking.pk)
        gd.delivery_date = timezone.localtime()
        gd.save()
        
        req = self.client.get(url, follow=True)
        assert b'Restituzione completata' in req.content
        
        # breakpoint()
        # print(req.content.decode())
        

    # def test_altro(self):
        # breakpoint()
        # print(req.content.decode())


