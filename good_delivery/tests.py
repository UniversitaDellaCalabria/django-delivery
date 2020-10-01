import logging
import urllib

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.test.client import RequestFactory
from django.urls import reverse
from django.utils import timezone

from . forms import *
from . models import *
from . settings import GOOD_STOCK_FORMS_PREFIX
from . templatetags.good_delivery_tags import (current_date,
                                               markdown,
                                               user_from_pk)
from . views import _generate_good_delivery_token_email
from . utils import open_html_in_webbrowser


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

_user_admin = dict(username='admin', password='admin',
                   is_superuser=1, is_staff=1)
_user_op = dict(username='ciro', email='thatmail@ingoalla.org')
_user = dict(username='utonto', email='thatmail@utonti.org')

_stock_prefix = getattr(settings, "GOOD_STOCK_FORMS_PREFIX",
                                 GOOD_STOCK_FORMS_PREFIX)
_item_data = {'{}1'.format(_stock_prefix): 1,
              'document_type': 'that_doc',
              'document_id': 'CICI',
              'notes': ''}

campaign_data = dict(name='banane',
                     date_start=timezone.localtime(),
                     date_end=timezone.localtime() + timezone.timedelta(hours=3),
                     is_active=True,
                     require_agreement=False,
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
        data['require_agreement'] = True
        data['identity_document_required'] = True
        campaign = DeliveryCampaign.objects.create(**data)
        devpoint = DeliveryPoint.objects.create(campaign=campaign,
                                                name='ufficio_gear')

        op_devpoint = OperatorDeliveryPoint.objects.create(delivery_point=devpoint,
                                                           operator=self.operator)
        good_devpoint_stock = DeliveryPointGoodStock.objects.create(delivery_point=devpoint,
                                                              good=self.good_gear,
                                                              max_number=0)
        good_devpoint_stock_identifier = DeliveryPointGoodStockIdentifier.objects.create(
                                            delivery_point_stock = good_devpoint_stock,
                                            good_identifier = 23,
                                        )
        booking = GoodDelivery.objects.create(delivery_point=devpoint,
                                              delivered_to=self.user,
                                              choosen_delivery_point=op_devpoint.delivery_point,
                                              campaign=campaign)
        return booking, good_devpoint_stock


    def test_op_gear(self):
        self.client.force_login(self.operator)

        url = reverse('good_delivery:operator_active_campaigns')
        home = self.client.get(url)
        assert b'non abilitato' in home.content

        campaign_booking, good_devpoint_stock = self._campaign_gear()
        home = self.client.get(url, follow=True)
        assert b'Prenotazioni da gestire' in home.content


    def _get_csrfmiddlewaretoken(self, context):
        """
        context = self.client.get().context
        returns a POSTable data dict
        """
        csrfmiddlewaretoken = context.get('csrf_token').__str__()
        return {'csrfmiddlewaretoken': csrfmiddlewaretoken}


    def test_op_multiple_delivery_points(self):
        campaign_booking, good_devpoint_stock = self._campaign_gear()
        devpoint = DeliveryPoint.objects.create(campaign=good_devpoint_stock.delivery_point.campaign,
                                                name='ufficio_gear2')
        op_devpoint = OperatorDeliveryPoint.objects.create(delivery_point=devpoint,
                                                           operator=self.operator)
        self.client.force_login(self.operator)
        url_kwargs = dict(campaign_id=good_devpoint_stock.delivery_point.campaign.slug)
        url = reverse('good_delivery:operator_campaign_detail',
                      kwargs=url_kwargs)
        req = self.client.get(url)
        assert b'Prenotazioni da gestire' in req.content


    def test_op_create_delivery(self):
        """
        cannot do that, only booked delivery allowed
        """
        self.client.force_login(self.operator)
        campaign_booking, good_devpoint_stock = self._campaign_gear()

        url_kwargs = dict(campaign_id=good_devpoint_stock.delivery_point.campaign.slug,
                          delivery_point_id=good_devpoint_stock.delivery_point.pk)
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
        
        # test items availability without a real stock
        good_devpoint_stock.get_available_items()
        
        url_kwargs = dict(campaign_id=op_devpoint.delivery_point.campaign.slug,
                          delivery_point_id=good_devpoint_stock.delivery_point.pk)
        url = reverse('good_delivery:operator_new_delivery',
                      kwargs=url_kwargs)
        req = self.client.get(url, follow=True)
        assert b'Nuova consegna' in req.content

        csrf_data = self._get_csrfmiddlewaretoken(req.context)
        data = {'quantity': 1, 'user': self.user.pk}
        data.update(csrf_data)
        req = self.client.post(url, data=data, follow=True)

        csrf_data = self._get_csrfmiddlewaretoken(req.context)
        data = {'1': 1, 'user': self.user.pk}
        data.update(csrf_data)
        req = self.client.post(url, data=data, follow=True)

        assert req.status_code == 200
        assert b'con successo' in req.content
        
        # manual operator_good_delivery_deliver
        good_delivery_id = GoodDelivery.objects.filter(delivered_to=self.user).first()
        url_kwargs = dict(campaign_id=op_devpoint.delivery_point.campaign.slug,
                          delivery_point_id=good_devpoint_stock.delivery_point.pk,
                          good_delivery_id=good_delivery_id.pk)
        url = reverse('good_delivery:operator_good_delivery_deliver',
                      kwargs=url_kwargs)
        req = self.client.get(url, follow=True)
        assert b'Prenotazioni da gestire' in req.content


    def _get_operator_good_delivery_detail(self):
        self.client.force_login(self.operator)
        campaign_booking, good_devpoint_stock = self._campaign_gear()
        url_kwargs = dict(campaign_id=good_devpoint_stock.delivery_point.campaign.slug,
                          delivery_point_id=good_devpoint_stock.delivery_point.pk,
                          good_delivery_id=campaign_booking.pk)
        url = reverse('good_delivery:operator_good_delivery_detail',
                       kwargs=url_kwargs)
        return url, campaign_booking, good_devpoint_stock


    def test_op_update_booked_delivery(self):
        url, campaign_booking, good_devpoint_stock = \
            self._get_operator_good_delivery_detail()
        req = self.client.get(url, follow=True)
        assert req.status_code == 200

        # redirect to add-items
        url = req.redirect_chain[0][0]

        ## test form
        data = _item_data.copy()        
        # test missing documents
        csrf_data = self._get_csrfmiddlewaretoken(req.context)
        data.update(csrf_data)
        
        data.pop('document_id')
        req = self.client.post(url, data=data, follow=True)
        assert b'Inserisci gli estremi' in req.content
        
        # test invalid quantities
        data = _item_data.copy()
        data['{}1'.format(_stock_prefix)] = '1.2'
        csrf_data = self._get_csrfmiddlewaretoken(req.context)
        data.update(csrf_data)
        req = self.client.post(url, data=data, follow=True)
        assert b'reali' in req.content
        
        # test buono
        data = _item_data.copy()
        csrf_data = self._get_csrfmiddlewaretoken(req.context)
        data.update(csrf_data)
        req = self.client.post(url, data=data, follow=True)
        assert b'Invia link attivazione' in req.content

        url_kwargs = dict(campaign_id=good_devpoint_stock.delivery_point.campaign.slug,
                          delivery_point_id=good_devpoint_stock.delivery_point.pk,
                          good_delivery_id=campaign_booking.pk)
        url = reverse('good_delivery:operator_good_delivery_send_token',
              kwargs=url_kwargs)
        req = self.client.get(url, follow=True)
        assert b'Link di attivazione inviato' in req.content

        gd = GoodDelivery.objects.get(pk=campaign_booking.pk)
        assert gd.state == 'in attesa'

        # insert stock identifiers        
        url_kwargs = dict(campaign_id=good_devpoint_stock.delivery_point.campaign.slug,
                          delivery_point_id=good_devpoint_stock.delivery_point.pk,
                          good_delivery_id=campaign_booking.pk)
        url = reverse('good_delivery:operator_good_delivery_detail',
              kwargs=url_kwargs)
        
        # Wrong identifiers
        data = {'form1-good_stock_identifier': 'asas',
                'form1-good_identifier': 23.345345345}
        csrf_data = self._get_csrfmiddlewaretoken(req.context)
        data.update(csrf_data)
        req = self.client.post(url, data=data, follow=True)
        assert b'non compare tra quelle' in req.content

        # good identifiers
        data = {'form1-good_stock_identifier': 1,
                'form1-good_identifier': 23}
        csrf_data = self._get_csrfmiddlewaretoken(req.context)
        data.update(csrf_data)
        req = self.client.post(url, data=data, follow=True)
        assert 'Quantità: 1' in req.content.decode()
        
        ## user access
        self.client.force_login(self.user)
        url = reverse('good_delivery:user_index')
        home = self.client.get(url)
        assert b'In corso' in home.content
        

    def test_op_delivery_campaign_expired(self):
        url, campaign_booking, good_devpoint_stock = \
            self._get_operator_good_delivery_detail()

        req = self.client.get(url, follow=True)
        csrf_data = self._get_csrfmiddlewaretoken(req.context)

        ## test campaign not in progress
        campaign_booking.campaign.date_end = timezone.localtime() - \
                                             timezone.timedelta(days=1024)
        campaign_booking.campaign.save()
        assert not campaign_booking.campaign.is_in_progress()

        req = self.client.post(url, data=csrf_data, follow=True)
        assert b'Campagna non in corso' in req.content


    def test_op_delivery_not_waiting(self):
        url, campaign_booking, good_devpoint_stock = \
            self._get_operator_good_delivery_detail()
        req = self.client.get(url, follow=True)
        csrf_data = self._get_csrfmiddlewaretoken(req.context)

        campaign_booking.disabled_date = timezone.localtime()
        campaign_booking.save()
        assert not campaign_booking.is_waiting()

        # good_delivery hasn't items!
        # so view redirect to operator_good_delivery_add_items
        #
        req = self.client.post(url, data=csrf_data, follow=True)
        assert b'disabilitata' in req.content


    def test_op_delivery_disable(self):
        _, campaign_booking, good_devpoint_stock = \
            self._get_operator_good_delivery_detail()
        url_kwargs = dict(campaign_id=campaign_booking.campaign.slug,
                          delivery_point_id=good_devpoint_stock.delivery_point.pk,
                          good_delivery_id=campaign_booking.pk)
        url = reverse('good_delivery:operator_good_delivery_disable',
                      kwargs=url_kwargs)

        req = self.client.get(url, follow=True)

        csrf_data = self._get_csrfmiddlewaretoken(req.context)
        data = {'notes': 'notes'}
        data.update(csrf_data)
        req = self.client.post(url, data=data, follow=True)

        gd = GoodDelivery.objects.get(pk=campaign_booking.pk)
        assert gd.disabled_date
        assert gd.state == 'disabilitata'
        assert b'Disabilitazione completata' in req.content


    def test_op_delivery_delete(self):
        _, campaign_booking, good_devpoint_stock = \
            self._get_operator_good_delivery_detail()
        url_kwargs = dict(campaign_id=campaign_booking.campaign.slug,
                          delivery_point_id=good_devpoint_stock.delivery_point.pk,
                          good_delivery_id=campaign_booking.pk)
        url = reverse('good_delivery:operator_good_delivery_delete',
                      kwargs=url_kwargs)

        req = self.client.get(url, follow=True)
        assert GoodDelivery.objects.filter(pk=campaign_booking.pk)
        assert b'Eliminazione non consentita' in req.content

        url = reverse('good_delivery:operator_good_delivery_send_token',
                      kwargs=url_kwargs)
        req = self.client.get(url, follow=True)
        # campaign_booking hasn't items!
        # so is_waiting() return an empty queryset
        # so operator_good_delivery_send_token returns "Consegna bloccata" message
        assert 'Consegna bloccata' in req.content.decode()


    # def test_op_delivery_preload(self):
        # """
        # if booking required will be not available
        # """
        # _, campaign_booking, good_devpoint_stock = \
            # self._get_operator_good_delivery_detail()
        # url_kwargs = dict(campaign_id=campaign_booking.campaign.slug)
        # url = reverse('good_delivery:operator_new_delivery_preload',
                      # kwargs=url_kwargs)
        # req = self.client.get(url, follow=True)
        # assert req.status_code == 403

        # campaign_booking.campaign.operator_can_create = True
        # campaign_booking.campaign.save()
        # req = self.client.get(url, follow=True)
        # assert b'Nuova consegna' in req.content

        # csrf_data = self._get_csrfmiddlewaretoken(req.context)
        # ## first try, failed csrf
        # data = dict()
        # data.update(csrf_data)
        # data['good_stock'] = 1
        # data['user'] = 2
        # req = self.client.post(url, data=data, follow=True)
        # assert b'inserito con successo' in req.content


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
        url_kwargs = dict(campaign_id=campaign_booking.campaign.slug,
                          delivery_point_id=good_devpoint_stock.delivery_point.pk,
                          good_delivery_id=campaign_booking.pk)
        url = reverse('good_delivery:operator_another_delivery',
                      kwargs=url_kwargs)
        req = self.client.get(url, follow=True)
        assert b'Processi di consegna attivi' in req.content
        
        ## disable
        gd = GoodDelivery.objects.get(pk=campaign_booking.pk)
        gd.disabled_date = timezone.localtime()
        gd.save()
        
        url = reverse('good_delivery:operator_good_delivery_disable',
              kwargs=url_kwargs)
        req = self.client.get(url, follow=True)
        assert b'disabilitata' in req.content
        
        ## POST disabilita
        csrf_data = self._get_csrfmiddlewaretoken(req.context)
        data = {'notes': 'test'*10000}
        data.update(csrf_data)
        req = self.client.post(url, data=data, follow=True)
        
        assert b'Disabilitazione completata' in req.content
        assert req.status_code == 200

        # deliver again
        url = reverse('good_delivery:operator_another_delivery',
                      kwargs=url_kwargs)
        data = _item_data.copy()
        csrf_data = self._get_csrfmiddlewaretoken(req.context)
        data.update(csrf_data)
        req = self.client.post(url, data=data, follow=True)
        # assert b'disabilitata senza beni inseriti' in req.content
        
        # TODO
        #open_html_in_webbrowser(req.content)
        
        
    # def test_operator_good_delivery_return(self):
        # _, campaign_booking, good_devpoint_stock = \
            # self._get_operator_good_delivery_detail()
        # url_kwargs = dict(campaign_id=campaign_booking.campaign.slug,
                          # good_delivery_id=campaign_booking.pk)
        # url = reverse('good_delivery:operator_good_delivery_return',
                      # kwargs=url_kwargs)

        # ## this covers the check
        # req = self.client.get(url, follow=True)
        # assert b'Consegna non ancora effettuata' in req.content

        # gd = GoodDelivery.objects.get(pk=campaign_booking.pk)
        # gd.delivery_date = timezone.localtime()
        # gd.save()

        # req = self.client.get(url, follow=True)
        # assert b'Restituzione completata' in req.content

        # gd.return_date = timezone.localtime()
        # gd.save()
        # req = self.client.get(url, follow=True)
        # assert b'Bene precedentemente restituito' in req.content

    def test_user_use_token(self):
        url, campaign_booking, good_devpoint_stock = \
            self._get_operator_good_delivery_detail()

        ## user access
        self.client.force_login(self.user)
        url = reverse('good_delivery:user_index')
        home = self.client.get(url)
        assert b'In corso' in home.content

        ## user uses token
        req_factory = RequestFactory()
        request = req_factory.get(url)
        gd = GoodDelivery.objects.get(pk=campaign_booking.pk)
        token = _generate_good_delivery_token_email(request, gd)

        url = reverse('good_delivery:user_use_token')
        req = self.client.get(url, data={'token': token})
        assert req.status_code == 401
        assert b'Consegna non completata' in req.content

        gd.delivered_by = self.operator
        gd.save()

        req = self.client.get(url, data={'token': token})
        assert b'Hai confermato' in req.content

    def test_datatables(self):
        url, campaign_booking, good_devpoint_stock = \
            self._get_operator_good_delivery_detail()

        ## user access
        self.client.force_login(self.operator)
        
        url = reverse('good_delivery:delivery_point_deliveries_json',
                      kwargs=dict(campaign_id = campaign_booking.campaign.slug,
                                  delivery_point_id = good_devpoint_stock.delivery_point.pk))
        data = json.dumps({"draw":1,
                          "columns":[
                            {"data":0,"name":"","searchable":1,"orderable":1,"search":{"value":"","regex":0}},
                            {"data":1,"name":"","searchable":1,"orderable":0,"search":{"value":"","regex":0}},
                            {"data":2,"name":"","searchable":1,"orderable":0,"search":{"value":"","regex":0}},
                            {"data":3,"name":"","searchable":1,"orderable":0,"search":{"value":"","regex":0}},
                            {"data":4,"name":"","searchable":1,"orderable":0,"search":{"value":"","regex":0}}
                            ],
                          "order":[{"column":0,"dir":"asc"}],
                          "start":"0",
                          "length":"10",
                          "search": {"value": '''{"text":"", "delivery_point": null}''', "regex":0}})
        req = self.client.post(url, dict(args =data))
        content = json.loads(req.content)
        assert isinstance(content, dict)

    # def test_altro(self):
        # breakpoint()
        # print(req.content.decode())


