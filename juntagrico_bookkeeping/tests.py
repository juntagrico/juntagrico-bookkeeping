import django.test
from datetime import date
from juntagrico.models import *
from juntagrico_bookkeeping.models import *
from juntagrico_bookkeeping.bookkeeping_logic import *

class SubscriptionTestBase(django.test.TestCase):
    def setUp(self):
        member = Member.objects.create(
            first_name = "Michael",
            last_name = "Test",
            email = "test@test.ch",
            addr_street = "Musterstrasse",
            addr_zipcode = "8000",
            addr_location = "Zürich",
            phone = "01234567"
            )

        subs_size = SubscriptionSize.objects.create(
            name = "Normal",
            long_name = "Normale Grösse",
            size = 1
            )

        subs_type = SubscriptionType.objects.create(
            name="Normal",
            size = subs_size,
            shares = 1,
            required_assignments = 5,
            price = 1200,
            )

        depot = Depot.objects.create(
            code = "Depot 1",
            name = "Das erste Depot",
            contact = member,
            weekday = 5,
            )

        self.subs = Subscription.objects.create(
            depot = depot,
            primary_member = member,
            active = True,
            activation_date = date(2018, 1, 1)
            )
        TSST.objects.create(
            subscription = self.subs,
            type = subs_type
            )

        extrasub_category = ExtraSubscriptionCategory.objects.create(
            name = "ExtraCat1"
            )

        extrasub_type = ExtraSubscriptionType.objects.create(
            name = "Extra 1",
            size = "Extragross",
            description = "Extra Subscription",
            category = extrasub_category
            )

        extrasub_period1 = ExtraSubBillingPeriod.objects.create(
            type = extrasub_type,
            price = 100,
            start_day = 1,
            start_month = 1,
            end_day = 30,
            end_month = 6,
            cancel_day = 31,
            cancel_month = 5
            )
        extrasub_period2 = ExtraSubBillingPeriod.objects.create(
            type = extrasub_type,
            price = 200,
            start_day = 1,
            start_month = 7,
            end_day = 31,
            end_month = 12,
            cancel_day = 30,
            cancel_month = 11
            )

        self.extrasubs = ExtraSubscription.objects.create(
            main_subscription = self.subs,
            active = True,
            activation_date = date(2018,1,1),
            type = extrasub_type
            )

        # create account for member
        MemberAccount.objects.create(
            member = member,
            account = "4321"
            )


        Settings.objects.create(
            debtor_account = "1100"
            )


class SuscriptionLogicTest(SubscriptionTestBase):

    def test_price_by_date_fullyear(self):
        start_date = date(2018, 1, 1)
        end_date = date(2018, 12, 31)
        price_fullyear = subscription_price_by_date(self.subs, start_date, end_date)
        self.assertEqual(1200.0, price_fullyear, "full year")

    def test_price_by_date_quarter(self):
        start_date = date(2018, 4, 1)
        end_date = date(2018, 6, 30)
        price_quarter = subscription_price_by_date(self.subs, start_date, end_date)
        price_quarter_expected = 1200.0 * (30 + 31 + 30) / 365
        self.assertEqual(price_quarter_expected, price_quarter, "second quarter")

    def test_price_by_date_partial_subscription(self):
        self.subs.activation_date = date(2018, 7, 1)
        self.subs.deactivation_date = date(2018, 9, 30)
        start_date = date(2018, 1, 1)
        end_date = date(2018, 12, 31)
        price = subscription_price_by_date(self.subs, start_date, end_date)
        price_expected = 1200.0 * (31 + 31 + 30) / 365
        self.assertEqual(price_expected, price, "quarter subscription over a year")

    def test_subscription_booking_full_year(self):
        start_date = date(2018, 1, 1)
        end_date = date(2018, 12, 31)
        bookings_list = subscription_bookings_by_date(start_date, end_date)
        self.assertEqual(1, len(bookings_list))
        self.assertEqual(1200.0, bookings_list[0].price)
        self.assertEqual(start_date, bookings_list[0].date)
        self.assertEqual("180101000000001000000001", bookings_list[0].docnumber)

    def test_subscription_booking_part_year(self):
        start_date = date(2018, 1, 1)
        end_date = date(2018, 12, 31)
        # modify subscription to last from 1.7. - 30.09.
        self.subs.activation_date = date(2018, 7, 1)
        self.subs.deactivation_date = date(2018, 9, 30)
        self.subs.save()
        bookings_list = subscription_bookings_by_date(start_date, end_date)
        self.assertEqual(1, len(bookings_list))
        booking = bookings_list[0]
        price_expected = 1200.0 * (31 + 31 + 30) / 365
        self.assertEqual(price_expected, booking.price)
        self.assertEqual(date(2018, 7, 1), booking.date)
        self.assertEqual("180101000000001000000001", booking.docnumber)
        self.assertEqual("1100", booking.debit_account)
        self.assertEqual("", booking.credit_account)     # subscriptiontype account is not assigned
        self.assertEqual("4321", booking.member_account)

    def test_generate_document_number_for_subscription(self):
        docnumber = gen_document_number(self.subs, date(2018, 1, 1))
        docnumber_expected = "180101000000001000000001"
        self.assertEqual(docnumber_expected, docnumber, "document_number for subscription")


class ExtraSubscriptionLogicTest(SubscriptionTestBase):

    def test_price_by_date_fullyear(self):
        start_date = date(2018, 1, 1)
        end_date = date(2018, 12, 31)
        price = extrasub_price_by_date(self.extrasubs, start_date, end_date)
        price_expected = 300
        self.assertEqual(price_expected, price, "extra subscription full year")

    def test_price_by_date_overlapping(self):
        start_date = date(2018, 6,1)
        end_date = date(2018, 9, 30)
        price = extrasub_price_by_date(self.extrasubs, start_date, end_date)
        price_expected = (100.0 * 30 / (31 + 28 + 31 + 30 + 31 + 30)) +\
                        (200.0 * (31 + 31 + 30) / (31 + 31 + 30 + 31 + 30 + 31))
        self.assertEqual(price_expected, price, "extra subscription june - september")

    def test_generate_document_number_for_extra_subscription(self):
        docnumber = gen_document_number(self.extrasubs, date(2018, 1, 1))
        docnumber_expected = "180101000000001000000002"
        self.assertEqual(docnumber_expected, docnumber, "document_number for extra subscription")


    def test_bookings_full_year(self):
        start_date = date(2018, 1, 1)
        end_date = date(2018, 12, 31)
        bookings_list = extrasub_bookings_by_date(start_date, end_date)
        self.assertEqual(1, len(bookings_list))
        booking = bookings_list[0]
        self.assertEqual(300, booking.price)
        self.assertEqual(date(2018, 1, 1), booking.date)
        self.assertEqual("180101000000001000000002", booking.docnumber)
        self.assertEqual("1100", booking.debit_account)
        self.assertEqual("", booking.credit_account)     # subscriptiontype account is not assigned
        self.assertEqual("4321", booking.member_account)



