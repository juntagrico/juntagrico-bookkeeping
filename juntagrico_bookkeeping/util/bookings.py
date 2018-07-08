# -*- coding: utf-8 -*-
from datetime import date
from juntagrico.models import Subscription, ExtraSubscription
from juntagrico.dao.subscriptiondao import SubscriptionDao
from juntagrico.util.bills import scale_subscription_price
from juntagrico_bookkeeping.models import Settings

def subscription_bookings_by_date(fromdate, tilldate):
    """
    Generate a list of booking for subscriptions.
    For each type that is assigned to a subscription, a separate booking
    is generated.
    """
    subscriptions = SubscriptionDao.subscriptions_by_date(fromdate, tilldate)
    
    # global debtor account on settings object
    debtor_account = Settings.objects.first().debtor_account

    bookings = []
    for subs in subscriptions:
        for subs_type in subs.types.all():
            booking = Booking()
            booking.date = max(fromdate, subs.activation_date or date.min)
            booking.activation_date = subs.activation_date
            booking.deactivation_date = subs.deactivation_date
            booking.docnumber = gen_document_number(subs, fromdate)
            booking.member = subs.primary_member
            booking.text = "Abo: %s, %s" % (subs_type, subs.primary_member)
            eff_start = max(fromdate, subs.activation_date or date.min)
            eff_end = min(tilldate, subs.deactivation_date or date.max)
            if (eff_start > fromdate) or (eff_end < tilldate):
                # subscription is activated or deactivate inside our interval
                # set special marker price and mention interval in text
                booking.price = 0.99
                booking.text = "%s, Teilperiode %s - %s" % (booking.text,
                    eff_start.strftime("%d.%m.%y"), eff_end.strftime("%d.%m.%y"))
            else:
                booking.price = scale_subscription_price(subs, fromdate, tilldate)            
            # accounts
            booking.debit_account = debtor_account  # soll: debitor-konto
            if hasattr(subs_type, "subscriptiontype_account"):
                booking.credit_account = subs_type.subscriptiontype_account.account
            else:
                booking.credit_account = ""
            if hasattr(subs.primary_member, "member_account"):
                booking.member_account = subs.primary_member.member_account.account
            else:
                booking.member_account = "" 

            bookings.append(booking)
    return bookings

def extrasubscriptions_by_date(fromdate, tilldate):
    """
    subscriptions that are active in a certain period
    all subscriptions except those that ended before or 
    started after our date range.
    """
    return ExtraSubscription.objects.exclude(deactivation_date__lt=fromdate).exclude(activation_date__gt=tilldate)

def extrasub_price_by_date(extrasub, fromdate, tilldate):
    """
    calculate price for a certain date interval.
    """
    if fromdate.year != tilldate.year:
        raise Exception("price_by_date interval must be in one year.")
    price = 0.0

    # iterate over extra subscription periods and sum price parts
    for period in extrasub.type.periods.all():
        period_start = date(fromdate.year, period.start_month, period.start_day)
        period_end = date(fromdate.year, period.end_month, period.end_day)
        part_start = max(period_start, fromdate)
        part_end = min(period_end, tilldate) 

        part_price = float(period.price) * ((part_end - part_start).days + 1) / ((period_end - period_start).days + 1)
        price += part_price

    return price

def extrasub_bookings_by_date(fromdate, tilldate):
    """
    Generate a list of booking for extra subscriptions.
    """
    extrasubs = extrasubscriptions_by_date(fromdate, tilldate)
    
    # global debtor account on settings object
    debtor_account = Settings.objects.first().debtor_account

    bookings = []
    for subs in extrasubs:
        booking = Booking()
        booking.price = extrasub_price_by_date(subs, fromdate, tilldate)
        booking.date = max(fromdate, subs.activation_date or date.min)
        booking.activation_date = subs.activation_date
        booking.deactivation_date = subs.deactivation_date
        booking.docnumber = gen_document_number(subs, fromdate)
        booking.member = subs.main_subscription.primary_member
        booking.text = "Zusatz: %s, %s" % (subs.type, booking.member)
        booking.debit_account = debtor_account  # soll: debitor-konto
        if hasattr(subs.type.category, "extrasub_account"):
            booking.credit_account = subs.type.category.extrasub_account.account
        else:
            booking.credit_account = ""
        if hasattr(subs.main_subscription.primary_member, "member_account"):
            booking.member_account = subs.main_subscription.primary_member.member_account.account
        else:
            booking.member_account = "" 

        bookings.append(booking)
    return bookings


def gen_document_number(entry, range_start):
    """
    Generate document number for booking a suscription or extra subscription.
    The generated document number is affected by the start-date of the booking period, so
    that each subscription gets a unique document number per booking period.

    Structure of document number:
    YYMMDD<id of subcription 9-digits>
    """
    date_part = range_start.strftime('%y%m%d')
    if hasattr(entry, 'primary_member'):
        member = entry.primary_member
    else:
        member = entry.main_subscription.primary_member
    member_part = str(member.id).rjust(9, '0')
    entry_part = str(entry.id).rjust(9, '0')
    return date_part + member_part + entry_part




class Booking (object):
    pass