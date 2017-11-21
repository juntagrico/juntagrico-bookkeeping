# unit tests for utils
import datetime
from io import BytesIO
from django.test import TestCase
from xlsxwriter import Workbook
from juntagrico_bookkeeping.xls import ExcelWriter
from juntagrico.models import MailTemplate

class ExcelWriterTest(TestCase):

    def test_write_list(self):
        data = [{
            'date_value': datetime.date(2017, 11, 21),
            'string_value': "Ächz",
            'int_value': 123,
            'float_value': 250.35
        },
        {
            'date_value': datetime.date(2017, 11, 30),
            'string_value': "blübber",
            'int_value': 541,
            'float_value': 1251.25
        }
        ]

        fields = [('date_value', 'Datums Wert'),
                  ('string_value', 'String Wert'),
                  ('int_value', 'Integer Wert'),
                  ('float_value', 'Float Wert')
                ]

        output = BytesIO()
        workbook = Workbook(output)
        writer = ExcelWriter(fields, workbook)
        writer.write_data(data)
        workbook.close()

        # we can't really test much here because xlswriter doesn't allow reading
        output.seek(0, 0)   # reset stream to beginning
        self.assertEquals(10, len(output.read(10)), "check for at least 10 bytes in excel output")


    def test_write_model(self):
        # create test data
        # we use mailing because it's the simplest model
        MailTemplate.objects.create(name = "test_mail1", template="some text", code="abc")
        MailTemplate.objects.create(name = "test_mail2", template="some other text", code="cde")

        fields = ("name", "template")

        output = BytesIO()
        workbook = Workbook(output)
        writer = ExcelWriter(fields, workbook)
        writer.write_data(MailTemplate)
        workbook.close()

        # we can't really test much here because xlswriter doesn't allow reading
        output.seek(0, 0)   # reset stream to beginning
        self.assertEquals(10, len(output.read(10)), "check for at least 10 bytes in excel output")
