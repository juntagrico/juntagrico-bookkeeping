# -*- coding: utf-8 -*-
from django.db.models import Sum
from django.shortcuts import render
from django import forms
from django.contrib.auth.decorators import permission_required
from juntagrico_bookkeeping.dao.subscriptiondao import SubscriptionDao

import datetime 

@permission_required('juntagrico.is_operations_group')
def subscriptions(request):
    """
    List of subscriptions
    """
    class DateRangeForm(forms.Form):
    	fromdate = forms.DateField()
    	tilldate = forms.DateField()

    form = DateRangeForm(request.GET)	

    if form.is_valid():
    	fromdate = form.cleaned_data['fromdate']
    	tilldate = form.cleaned_data['tilldate']
    else:
    	# if no daterange specified, default to last year
    	today = datetime.date.today()
    	fromdate = datetime.date(today.year-1, 1, 1)
    	tilldate = datetime.date(today.year-1, 12, 31)

    entities = SubscriptionDao.subscriptions_by_date(fromdate, tilldate) 
    # tried the following aggregation, but this would need an additional filter on bills
    # entities = entities.annotate(amount_billed=Sum('bills__amount'))

    def total_billed(subs):
        bills = SubscriptionDao.subscription_bills_by_date(subs, fromdate, tilldate)
        sum = 0.0
        for bill in bills:
            sum += bill.amount
        return sum


    subscriptions = [{  'activation_date': s.activation_date,
	        			'deactivation_date': s.deactivation_date,
	        			'primary_member': s.primary_member_nullsave(),
	        			'size': s.size,
	        			'size_name': s.size_name,
	        			'member_account': 'm_acct',
	        			'account': 'acct',
	        			'price': s.price,
	        			'amount_billed': total_billed(s) } for s in entities]    

    renderdict = {
    	'form_valid': form.is_valid(),
    	'form_errors': form.errors,
    	'fromdate': fromdate,
    	'tilldate': tilldate,
        'subscriptions': subscriptions
    }
    return render(request, "bk/subscriptions.html", renderdict)
