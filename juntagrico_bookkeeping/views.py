# -*- coding: utf-8 -*-
from django.shortcuts import render
from django import forms
from juntagrico.views import get_menu_dict
from juntagrico_bookkeeping.dao.subscriptiondao import SubscriptionDao

import datetime 

def parse_date(datestr):
	parts = datestr.split('-')
	if len(parts) != 3:
		raise Exception("invalid date value %s", datestr)
	return datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))	

# @login_required
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

    subscription_entities = SubscriptionDao.subscriptions_by_date(fromdate, tilldate) 
    print( subscription_entities )

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
	        			'amount_billed': total_billed(s) } for s in subscription_entities]    

    renderdict = get_menu_dict(request)
    renderdict.update({
    	'form_valid': form.is_valid(),
    	'form_errors': form.errors,
    	'fromdate': fromdate,
    	'tilldate': tilldate,
        'subscriptions': subscriptions
    })
    return render(request, "bk/subscriptions.html", renderdict)
