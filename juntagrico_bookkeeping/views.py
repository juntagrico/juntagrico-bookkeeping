import datetime 

from django.http import HttpResponse
from django.shortcuts import render
from django import forms
from django.contrib.auth.decorators import permission_required

from juntagrico_bookkeeping.dao.subscriptiondao import SubscriptionDao

from juntagrico.views import get_menu_dict
from juntagrico.models import Subscription
from juntagrico.util.temporal import start_of_business_year, start_of_next_business_year
from juntagrico.util.xls import generate_excell_load_fields


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
        subscriptions = SubscriptionDao.subscriptions_by_date(fromdate, tilldate)
    else:
        subscriptions = []   

    if request.GET.get('format', '') == "xlsx":
        return generate_excel(subscriptions)
    else:    
        renderdict = get_menu_dict(request)
        renderdict .update({
            'daterange_form': daterange_form,
            'subscriptions': subscriptions
        })
        return render(request, "bk/subscriptions.html", renderdict)



def generate_excel(subscriptions):
    
    fields ={
        'activation_date':'',
        'deactivation_date':'',
        'primary_member':'AbonnentIn',
        'size':'Grösse',
        'primary_member.member_allocation.allocation':'Konto Mitglied',
        'subscription_allocation.allocation':'Konto Abo',
        'price':'Beitrag',
        'amount_billed':'Rechnung',
    }

    return generate_excell_load_fields(fields, Subscription, subscriptions)
