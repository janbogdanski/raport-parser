from unittest import TestCase
from record import Record
from sap_record import SapRecord
from printer_record import PrinterRecord

__author__ = 'jan.bogdanski'


class TestRecord(TestCase):

    test_floats = [
        {
            'input': '100',
            'expected': 100.
        },
        {
            'input': '1,32',
            'expected': 1.32
        },
        {
            'input': '1.000,55',
            'expected': 1000.55
        },
        {
            'input': '24.600,00',
            'expected': 24600.00
        },
        {
            'input': ' 1.191.991,17 ',
            'expected': 1191991.17
        },
        {
            'input': '1000,5531',
            'expected': 1000.55
        },


    ]

    rounds = [
        {
            'input': '1000.5531',
            'expected': 1000.55
        },
        {
            'input': '1000.5571',
            'expected': 1000.56
        },
        {
            'input': '1000.555',
            'expected': 1000.55
        },
        {
            'input': '1000.5559',
            'expected': 1000.56
        },
    ]

    equals = {}

    @classmethod
    def setUpClass(cls):
        print 'setup'

        # set up data for equals test

        # wszystkie dane takie same i ok
        printer = PrinterRecord()
        sap = SapRecord()

        printer.sale_sum_by_tax = {'A': 28.0}
        printer.tax_sum_by_tax = {'A': 5.23}
        printer.total_tax_sum = 5.23

        sap.sale_sum_by_tax = {'A': -28.0}
        sap.tax_sum_by_tax = {'A': -5.23}
        sap.total_tax_sum = -5.23

        cls.equals["test1"] = {
            "sap": sap,
            "printer": printer,
            "expected": [{'status': 'OK', 'comment': '', 'message': Record.MESSAGE_ALL_OK, 'tax_symbol_err': None}]
        }

        # dodatkowy podatek C ktory nie zmienia wartosci podatkow (wynisi 0%)
        printer = PrinterRecord()
        sap = SapRecord()

        printer.sale_sum_by_tax = {'A': 28.0}
        printer.tax_sum_by_tax = {'A': 5.23}
        printer.total_tax_sum = 5.23

        sap.sale_sum_by_tax = {'A': -28.0, 'C': -2398488.75}
        sap.tax_sum_by_tax = {'A': -5.23, 'C': 0.0}
        sap.total_tax_sum = -5.23

        cls.equals["test2"] = {
            "sap": sap,
            "printer": printer,
            "expected": [{'status': 'BAD', 'comment': Record.MESSAGE_EQUAL_TAX_SUM, 'message': Record.MESSAGE_TAX_ONLY_SAP, 'tax_symbol_err': 'C'}]
        }

        # roznica 1grosza
        printer = PrinterRecord()
        sap = SapRecord()

        printer.sale_sum_by_tax = {'A': 28.0}
        printer.tax_sum_by_tax = {'A': 5.27}
        printer.total_tax_sum = 5.26

        sap.sale_sum_by_tax = {'A': -28.0}
        sap.tax_sum_by_tax = {'A': -5.23}
        sap.total_tax_sum = -5.23

        cls.equals["test3"] = {
            "sap": sap,
            "printer": printer,
            "expected": [{'status': 'BAD', 'comment': '', 'message': Record.MESSAGE_DIFFERENT_TAX_SUM, 'tax_symbol_err': 'A'}]

        }

        # technical code w zrzucie, suma podatkow zgodna
        printer = PrinterRecord()
        sap = SapRecord()

        printer.tax_sum_by_tax = {'A': 17.32}
        printer.total_tax_sum = 17.32

        sap.tax_sum_by_tax = {'A': -17.32, 'YA': 0.0}
        sap.total_tax_sum = -17.32
        cls.equals["test4"] = {
            "sap": sap,
            "printer": printer,
            "expected": [{'status': 'OK', 'comment': Record.MESSAGE_TECHNICAL_CODE, 'message': '', 'tax_symbol_err': None}]
        }

        # technical code w zrzucie, rozne wartosci innego podatku
        printer = PrinterRecord()
        sap = SapRecord()

        # printer.sale_sum_by_tax = {'A': 28.0}
        printer.tax_sum_by_tax = {'A': 0.36}
        printer.total_tax_sum = 0.36

        # sap.sale_sum_by_tax =
        sap.tax_sum_by_tax = {'A': -17.32, 'YA': 0.0, 'B': -0.67}
        sap.total_tax_sum = -17.99
        cls.equals["test5"] = {
            "sap": sap,
            "printer": printer,
            "expected": [{'status': 'BAD', 'comment': '', 'message': Record.MESSAGE_DIFFERENT_TAX_SUM, 'tax_symbol_err': 'A'},
                         {'status': 'BAD', 'comment': Record.MESSAGE_TECHNICAL_CODE, 'message': Record.MESSAGE_TAX_ONLY_SAP, 'tax_symbol_err': 'B'}]

        }

    # ##############################################################################################################################
    # ##############################################################################################################################

    # ##############################################################################################################################
    # ##############################################################################################################################

    def test_to_float(self):
        floats = self.test_floats
        for elem in floats:
            num = Record.to_float(elem["input"])
            self.assertEqual(num, elem["expected"])

    def test_round(self):
        rounds = self.rounds
        for elem in rounds:
            num = Record.round(elem["input"])
            self.assertEqual(num, elem["expected"])

    def test_equal_records(self):
        a = 'g'
        equals = self.equals
        for elem in equals:
            result = Record.equal_records(equals[elem]["printer"], equals[elem]["sap"])
            exp = result, equals[elem]["expected"]
            self.assertEqual(result, equals[elem]["expected"])
