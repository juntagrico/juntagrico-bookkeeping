# -*- coding: utf-8 -*-

from juntagrico.models import *


class SubscriptionDao:
    def __init__(self):
        pass

    @staticmethod
    def subscriptions_by_date(fromdate, tilldate):
        """
        all subscriptions except those that ended before or 
        started after our date range.
        """
        return Subscription.objects.exclude(deactivation_date__lt=fromdate)

    @staticmethod
    def subscription_bills_by_date(subscription, fromdate, tilldate):
        return subscription.bills.filter(bill_date__gte=fromdate, bill_date__lte=tilldate)


