from django.db import models

from juntagrico.models import *

class MemberAccount(models.Model):

    member = models.OneToOneField(Member, on_delete=models.CASCADE, related_name='member_account')
    account = models.CharField('Konto', max_length=100)
    
    def __str__(self):
        return self.member.get_name()

class SubscriptionTypeAccount(models.Model):

    subscriptiontype = models.OneToOneField(SubscriptionType, on_delete=models.CASCADE, related_name='subscriptiontype_account')
    account = models.CharField('Konto', max_length=100)
    
    def __str__(self):
        return self.subscriptiontype.primary_member.get_name()