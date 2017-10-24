# -*- coding: utf-8 -*-

from juntagrico.models import *
from django.db.models import Sum, Case, When

class SubscriptionDao:
    @staticmethod
    def subscriptions_by_date(fromdate, tilldate):
        """
        all subscriptions except those that ended before or 
        started after our date range.
        """
        subscriptions = Subscription.objects.exclude(deactivation_date__lt=fromdate).exclude(activation_date__gt=tilldate)
        with_amount_billed = subscriptions.annotate(amount_billed=Sum(Case(When(bills__bill_date__range=(fromdate, tilldate),then='bills__amount'))))
        return with_amount_billed

