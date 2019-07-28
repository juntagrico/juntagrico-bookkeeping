from juntagrico.util import addons

from juntagrico_bookkeeping.admin import *


addons.config.register_admin_menu('bk/bookkeeping_admin_menu.html')
addons.config.register_model_inline(Member, MemberAccountInline)
addons.config.register_model_inline(SubscriptionType, SubscriptionTypeAccountInline)
addons.config.register_model_inline(ExtraSubscriptionCategory, ExtraSubscriptionCategoryAccountInline)