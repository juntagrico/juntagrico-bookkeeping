from django.contrib import admin

from juntagrico_bookkeeping.entity.allocations import *

class MemberAllocationInline(admin.TabularInline):
    model = MemberAllocation
    verbose_name = 'Kontierung'
    verbose_name_plural = 'Kontierungen'
    extra = 0
    
class SubscriptionAllocationInline(admin.TabularInline):
    model = SubscriptionAllocation
    verbose_name = 'Kontierung'
    verbose_name_plural = 'Kontierungen'
    extra = 0