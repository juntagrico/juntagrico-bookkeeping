# -*- coding: utf-8 -*-
from django.shortcuts import render
from django import forms
from django.contrib.auth.decorators import permission_required
from juntagrico_bookkeeping.dao.subscriptiondao import SubscriptionDao
from juntagrico.util.temporal import start_of_business_year, start_of_next_business_year
from juntagrico_bookkeeping.xls import generate_excel
import datetime 
import types

@permission_required('juntagrico.is_operations_group')
def subscriptions(request):
    """
    List of subscriptions
    """
    class DateRangeForm(forms.Form):
        fromdate = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control'}))
        tilldate = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control'}))

    default_range = {
        'fromdate': start_of_business_year(),
        'tilldate': start_of_next_business_year() - datetime.timedelta(1)
        }

    if 'fromdate' in request.GET and 'tilldate' in request.GET:
        # request with query parameter
        daterange_form = DateRangeForm(request.GET)    
    else:
        daterange_form = DateRangeForm(default_range)

    if daterange_form.is_valid():
        fromdate = daterange_form.cleaned_data['fromdate']
        tilldate = daterange_form.cleaned_data['tilldate']
        entities = SubscriptionDao.subscriptions_by_date(fromdate, tilldate)
    else:
        entities = [] 

    subscriptions = [{  'activation_date': s.activation_date,
                        'deactivation_date': s.deactivation_date,
                        'primary_member': s.primary_member_nullsave(),
                        'size': s.size,
                        'size_name': s.size_name,
                        'member_account': 'm_account',
                        'account': 's_account',
                        'price': float(s.price),
                        'amount_billed': s.amount_billed } for s in entities]    

    if request.GET.get('format', '') == "xlsx":
        return excel_export(subscriptions)
    else:
        renderdict = {
            'daterange_form': daterange_form,
            'subscriptions': subscriptions
        }
        return render(request, "bk/subscriptions.html", renderdict)

def excel_export(subscriptions):
    fields = [
        ("activation_date", "Start"),
        ("deactivation_date", "Ende"),
        ("primary_member", "AbonnentIn"),
        ("size", "Anzahl"),
        ("size_name", "Bezeichnung"),
        ("member_account", "Konto AbonnentIn"),
        ("account", "Konto Abo"),
        ("price", "Beitrag"),
        ("amount_billed", "Rechnung")
    ]

    return generate_excel(fields, subscriptions, "Abos")

