from django.db import models
from juntagrico.entity import JuntagricoBaseModel
from juntagrico.entity.billable import Billable
from django.utils.translation import gettext as _


class Bill(JuntagricoBaseModel):
    '''
    Bill for a member.
    May contain amount for 1 billable subscription and / or
    some credit or debit offset (eg expenses or solidarity contributions).
    '''
    member = models.ForeignKey('juntagrico.Member', related_name='bills',
                null=False, blank=False,
                on_delete=models.PROTECT)
    bill_date = models.DateField(
        _('Rechnungsdatum'), null=False, blank=False)
    ref_number = models.CharField(
        _('Referenznummer'), max_length=30, unique=True)
    debtor_account = models.CharField(_('Debitorkonto'), max_length=10)

    # subscription
    billable = models.ForeignKey('juntagrico.Billable', related_name='bills',
                null=False, blank=False,
                on_delete=models.PROTECT)
    billable_amount = models.FloatField(_('Abobetrag'), null=False, blank=False)

    # offset
    OFFSET_NONE = 'NONE'
    OFFSET_CREDIT = 'CREDIT'
    OFFSET_DEBIT = 'DEBIT'
    offset_kind = models.CharField(_('Verrechnung'), max_length=6,
        null = False, blank = False,
        choices = [ (OFFSET_NONE, _('Keine')),
                    (OFFSET_CREDIT, _('Gutschrift')),
                    (OFFSET_DEBIT, _('Lastschrift')) ],
        default = OFFSET_NONE)
    offset_amount = models.FloatField(_('Verrechnungsbetrag'), null=False, blank=False)
    offset_text = models.CharField(_('Verrechnungstext'), max_length=50)
    offset_account = models.CharField(_('Verrechnungskonto'), max_length=10)

    # payment
    paid = models.BooleanField(_('bezahlt'), default=False)
    payment_date = models.DateField(
        _('Zahlungsdatum'), null=True, blank=True)
    payment_amount = models.FloatField(_('Zahlungsbetrag'), null=False, blank=False)

    def __str__(self):
        return '%s' % self.ref_number

    class Meta:
        verbose_name = _('Rechnung')
        verbose_name_plural = _('Rechnungen')


