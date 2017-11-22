from juntagrico_bookkeeping.admin import *

def admin_menu_template():
    return ['bk/bookkeeping_admin_menu.html']
    
def member_inlines():
    return [MemberAllocationInline]
    
def subscription_inlines():
    return [SubscriptionAllocationInline]