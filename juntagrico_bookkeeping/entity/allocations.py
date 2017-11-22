from django.db import models

from juntagrico.models import *

class MemberAllocation(models.Model):

    member = models.OneToOneField(Member, related_name='member_allocation')
    allocation = models.CharField('Kontierung', max_length=100)
    
    def __str__(self):
        return self.member.get_name()

class SubscriptionAllocation(models.Model):

    subscription = models.OneToOneField(Subscription, related_name='subscription_allocation')
    allocation = models.CharField('Kontierung', max_length=100)
    
    def __str__(self):
        return self.subscription.primary_member.get_name()