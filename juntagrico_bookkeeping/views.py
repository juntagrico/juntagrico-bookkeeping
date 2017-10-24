# -*- coding: utf-8 -*-
from django.shortcuts import render
from django import forms
from django.contrib.auth.decorators import permission_required
from juntagrico_bookkeeping.dao.subscriptiondao import SubscriptionDao
from juntagrico.util.temporal import start_of_business_year, start_of_next_business_year
import datetime 
from io import BytesIO
import xlsxwriter
from django.http import HttpResponse

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
                        'member_account': 'm_acct',
                        'account': 'acct',
                        'price': s.price,
                        'amount_billed': s.amount_billed } for s in entities]    

    if request.GET.get('format', '') == "xlsx":
        return generate_excel(fromdate, tilldate, subscriptions)
    else:
        renderdict = {
            'daterange_form': daterange_form,
            'subscriptions': subscriptions
        }
        return render(request, "bk/subscriptions.html", renderdict)


def generate_excel(fromdate, tilldate, subscriptions):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=Abos.xlsx'
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    fields = [
        ("Start", "activation_date" ),
        ("Ende", "deactivation_date"),
        ("AbonnentIn", "primary_member"),
        ("Anzahl", "size"),
        ("Bezeichnung", "size_name"),
        ("Konto AbonnentIn", "member_account"),
        ("Konto Abo", "account"),
        ("Beitrag", "price"),
        ("Rechnung", "amount_billed")
    ]

    # title
    

    # header row
    col = 0
    row = 0
    for label, fieldname in fields:
        worksheet.write_string(row, col, label)
        col += 1

    # data rows
    row = 2
    for subscription in subscriptions:
        col = 0
        for label, fieldname in fields:
            worksheet.write_string(row, col, str(subscription.get(fieldname, "")))
            col += 1
        row += 1

    workbook.close()
    response.write(output.getvalue())
    return response
