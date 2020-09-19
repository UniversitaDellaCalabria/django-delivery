import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from . models import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

_user_admin = dict(username='admin', password='admin', 
                   is_superuser=1, is_staff=1)
_user_op = dict(username='ciro', email='thatmail@ingoalla.org')
_user = dict(username='utonto', email='thatmail@utonti.org')

campaign_data = dict(name='banane',
                     date_start=timezone.localtime(),
                     date_end=timezone.localtime() + timezone.timedelta(hours=3),
                     is_active=1,
                     require_agreement=1)


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
        campaign = DeliveryCampaign.objects.create(**campaing_data)
        devpoint = DeliveryPoint.objects.create(campaign=campaign,
                                                name='ufficio_frutta')
        op_devpoint = OperatorDeliveryPoint.objects.create(delivery_point=devpoint,
                                                           operator=self.operator)
        good_devpoint = DeliveryPointGoodStock.objects.create(delivery_point=devpoint,
                                                              good=self.good_food,
                                                              max_number=0)
        return good_devpoint
        
    def _campaign_gear(self):
        data = campaign_data.copy()
        data['name'] = 'gears'
        campaign = DeliveryCampaign.objects.create(**data)
        devpoint = DeliveryPoint.objects.create(campaign=campaign,
                                                name='ufficio_gear')
        
        op_devpoint = OperatorDeliveryPoint.objects.create(delivery_point=devpoint,
                                                           operator=self.operator)
        good_devpoint = DeliveryPointGoodStock.objects.create(delivery_point=devpoint,
                                                              good=self.good_gear,
                                                              max_number=0)
        booking = UserDeliveryPoint.objects.create(delivery_point=devpoint,
                                                   user=self.user)
        return booking
    
    def test_op_gear(self):
        self.client.force_login(self.operator)
        
        url = reverse('good_delivery:operator_active_campaigns')
        home = self.client.get(url)
        assert b'non abilitato' in home.content
        
        campaign_booking = self._campaign_gear()
        url = reverse('good_delivery:operator_active_campaigns')
        home = self.client.get(url, follow=True)
        assert b'Prenotazioni da gestire' in home.content
        
        
