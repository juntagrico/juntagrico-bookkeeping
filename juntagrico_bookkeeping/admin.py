from django.contrib import admin

from juntagrico_bookkeeping.entity.account import *

class MemberAccountInline(admin.TabularInline):
    model = MemberAccount
    verbose_name = 'Konto'
    verbose_name_plural = 'Konti'
    extra = 0
    
class SubscriptionTypeAccountInline(admin.TabularInline):
    model = SubscriptionTypeAccount
    verbose_name = 'Konto'
    verbose_name_plural = 'Konti'
    extra = 0