from unittest import TestCase
from report_parser import ReportParser
from printer_record import PrinterRecord
from sap_record import SapRecord

__author__ = 'jan.bogdanski'


class TestParser(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser = ReportParser()
        cls.parser.args["date"] = "04.2015"
        cls.compare_test = {

            # test1 - both printer and sap equal - one record
            'test1': {
                "printer": {
                    '1000033619': PrinterRecord()
                },
                "sap": {
                    '1000033619': SapRecord()
                }
            },

            # test2 - both printer and sap equal - many record
            'test2': {
                "printer": {
                    '1000033619': PrinterRecord(),
                    '1000002266': PrinterRecord(),
                    '1000016406': PrinterRecord(),
                },
                "sap": {
                    '1000033619': SapRecord(),
                    '1000002266': SapRecord(),
                    '1000016406': SapRecord(),

                }
            },

            # test3 - only printer
            'test3': {
                "printer": {
                    '1000033619': PrinterRecord(),
                    '1000002266': PrinterRecord(),
                    '1000016406': PrinterRecord(),
                },
                "sap": {}
            },

            # test4 - only sap
            'test4': {
                "printer": {},
                "sap": {
                    '1000033619': SapRecord(),
                    '1000002266': SapRecord(),
                    '1000016406': SapRecord(),
                }
            },

            # test4 - only sap
            'test5': {
                "printer": {
                    '1000007346': PrinterRecord(),

                    '1000033619': PrinterRecord(),
                },
                "sap": {
                    '1000007346': SapRecord(),

                    '1000002266': SapRecord(),
                    '1000016406': SapRecord(),
                }
            },

        }

        printer = PrinterRecord()
        sap = SapRecord()

        printer.sale_sum_by_tax = {'A': 28.0}
        printer.tax_sum_by_tax = {'A': 5.23}
        printer.total_tax_sum = 5.23

        sap.sale_sum_by_tax = {'A': -28.0}
        sap.tax_sum_by_tax = {'A': -5.23}
        sap.total_tax_sum = -5.23

    def test_read_printer_report1(self):
        """
        test excluded receipts
        :return:
        """
        read = self.parser.read_printer_report(['files/printer1.txt'])
        self.assertEqual(len(read), 0)

    def test_read_printer_report2(self):
        """
        jeden prawidlowy rekord
        :return:
        """
        read = self.parser.read_printer_report(['files/printer2.txt'])
        self.assertEqual(len(read), 1)

    def test_read_printer_report3(self):
        """
        dwa prawidlowe rekordy
        :return:
        """
        read = self.parser.read_printer_report(['files/printer3.txt'])
        self.assertEqual(len(read), 2)

    def test_read_printer_report4(self):
        """
        prawidlowe i nieprawidlowe rekordy w printerze
        :return:
        """
        read = self.parser.read_printer_report(['files/printer4.txt'])
        self.assertEqual(len(read), 2)

    def test_read_sap_report1(self):
        """
        one valid record
        :return:
        # """
        SapRecord.FIRST_REPORT_LINE = 0
        read = self.parser.read_sap_report2('files/sap1.txt')

        expectet_refNum = '9100000003'

        self.assertEqual(len(read), 1)
        self.assertIn(expectet_refNum, read)
        self.assertEqual(read[expectet_refNum].tax_sum_by_tax, {'A': -210.93, 'YA': 0.0})
        self.assertEqual(read[expectet_refNum].total_tax_sum, -210.93)

    def test_read_sap_report2(self):
        """
        one valid record and sum row
        :return:
        # """
        SapRecord.FIRST_REPORT_LINE = 0
        read = self.parser.read_sap_report2('files/sap2.txt')

        expectet_refNum = '1000033619'

        self.assertEqual(len(read), 1)
        self.assertIn(expectet_refNum, read)
        self.assertEqual(read[expectet_refNum].tax_sum_by_tax, {'B': -12.33})
        self.assertEqual(read[expectet_refNum].total_tax_sum, -12.33)

    def test_get_common_elements1(self):
        both, only_printer, only_sap = self.parser.get_common_elements(self.compare_test["test1"]["printer"], self.compare_test["test1"]["sap"])
        self.assertEqual(len(both), 1)
        self.assertEqual(len(only_printer), 0)
        self.assertEqual(len(only_sap), 0)

    def test_get_common_elements2(self):
        both, only_printer, only_sap = self.parser.get_common_elements(self.compare_test["test2"]["printer"], self.compare_test["test2"]["sap"])
        self.assertEqual(len(both), 3)
        self.assertEqual(len(only_printer), 0)
        self.assertEqual(len(only_sap), 0)

    def test_get_common_elements3(self):
        both, only_printer, only_sap = self.parser.get_common_elements(self.compare_test["test3"]["printer"], self.compare_test["test3"]["sap"])
        self.assertEqual(len(both), 0)
        self.assertEqual(len(only_printer), 3)
        self.assertEqual(len(only_sap), 0)

    def test_get_common_elements4(self):
        both, only_printer, only_sap = self.parser.get_common_elements(self.compare_test["test4"]["printer"], self.compare_test["test4"]["sap"])
        self.assertEqual(len(both), 0)
        self.assertEqual(len(only_printer), 0)
        self.assertEqual(len(only_sap), 3)

    def test_get_common_elements5(self):
        both, only_printer, only_sap = self.parser.get_common_elements(self.compare_test["test5"]["printer"], self.compare_test["test5"]["sap"])
        self.assertEqual(len(both), 1)
        self.assertEqual(len(only_printer), 1)
        self.assertEqual(len(only_sap), 2)
