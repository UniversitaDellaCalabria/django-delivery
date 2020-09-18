from django import forms
from django.contrib import admin

from .models import *

class OperatorDeliveryPointInline(admin.TabularInline):
	 model = OperatorDeliveryPoint
	 extra = 0
