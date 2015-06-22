__author__ = 'jan.bogdanski'

eps = 0.000001

class Record (object):
    refNum = ''

    # suma sprzedazy na rachunku po typie podatku
    sale_sum_by_tax = {}

    # suma podatku od sprzedazy, po typie podatku
    tax_sum_by_tax = {}

    # calkowita suma podatku na rachunku
    total_tax_sum = 0

    # nieuzywane - suma brutto
    gross_sum = 0
    gross_prices = []

    # format daty na poszczegolnym typie zrodla (drukarka, sap)
    DATE_FORMAT = None

    STATUS_OK = 'OK'
    STATUS_BAD = 'BAD'

    MESSAGE_ALL_OK = "Zgodne wartosci podatkow "
    MESSAGE_TECHNICAL_CODE = "Technical code w zrzucie"
    MESSAGE_DIFFERENT_TAX_SUM = "Rozne kwoty podatku"
    MESSAGE_TAX_ONLY_PRINTER = "Podatek na rachunku tylko na drukarce"
    MESSAGE_TAX_ONLY_SAP = "Podatek na rachunku tylko w SAP"
    MESSAGE_ONLY_PRINTER = "Dokument o danym ID tylko na drukarce"
    MESSAGE_ONLY_SAP = "Dokument o danym ID tylko SAP"
    MESSAGE_EQUAL_TAX_SUM = "Sumy podatkow na rachunkach sa zgodne"

    # mapowanie stawek podatkowych, do unifikacji
    # w sapie sa A1, A2, na drukarce A, B, C
    tax_map = {
        "A1": "D",  # 5%
        "A2": "B",  # 8%
        "A8": "A",  # 23%
        "C0": "C",  # 0%
        "MWS": "A"  # 23% dziwne
    }

    def __init__(self):

        # inicjowanie pustymi wartosciami, cos nie tak bylo przy inicjowaniu
        # nowy obiekt tworzony w petli, mial wlasciwosci poprzedniego
        self.sale_sum_by_tax = {}
        self.tax_sum_by_tax = {}
        self.total_tax_sum = 0
        self.gross_sum = 0
        self.gross_prices = []

    @staticmethod
    def to_float(num):
        """
        convert US number style 1.191.991,17 to float
        :param num:
        :return:
        """
        if ',' in num:
            return round(float(num.replace('.', '').replace(',', '.').replace(' ', '')), 2)
        else:
            return round(float(num.replace(' ', '')), 2)

    @staticmethod
    def round(num):
        """
        convert input to float and round
        :param num:
        :return:
        """
        return round(float(num), 2)

    @staticmethod
    def equal_records(printer, sap):
        """
        @type printer: Record
        @type sap: Record
        """

        messages = []
        # message = {"tax_symbol_err": None, "status": None, "message": 'str', 'comment': 'comment'}
        printer_taxes = set(printer.tax_sum_by_tax.keys())
        sap_taxes = set(sap.tax_sum_by_tax.keys())

        taxes_in_both = printer_taxes.intersection(sap_taxes)
        taxes_in_printer = printer_taxes - sap_taxes
        taxes_in_sap = sap_taxes - printer_taxes

        # czy jest ok? Gdy rowne dlugosci tablic z tax, i ich odpowiednie wartosci rowne
        compare = [True if abs(abs(printer.tax_sum_by_tax[tax]) - abs(sap.tax_sum_by_tax[tax])) <= eps else False
                   for tax in taxes_in_both if len(taxes_in_both) == len(sap_taxes)]
        if len(compare) and all(compare):
            messages.append({
                "tax_symbol_err": None,
                "status": Record.STATUS_OK,
                "message": Record.MESSAGE_ALL_OK,
                "comment": ""
            })
            # globalnie ok, mozna zrobic return
            return messages

        # technical code YA nie dyskwalifikuje - jesli suma podatkow jest ok, to od razu return
        if sap.TAX_TECHNICAL_CODE in taxes_in_sap\
                and abs(abs(printer.total_tax_sum) - abs(sap.total_tax_sum)) < eps:
            messages.append({
                "tax_symbol_err": None,
                "status": Record.STATUS_OK,
                "message": "",
                "comment": Record.MESSAGE_TECHNICAL_CODE
            })
            # globalnie ok, mozna zrobic return
            return messages

        # sprawdzenie sum poszczegolnych wartosci podatkow
        # return dopiero na koniec if'ow
        comment = ""
        if abs(abs(printer.total_tax_sum) - abs(sap.total_tax_sum)) <= eps:
            comment = Record.MESSAGE_EQUAL_TAX_SUM
        if len(taxes_in_both):
            for tax in taxes_in_both:
                diff = abs(abs(printer.tax_sum_by_tax[tax]) - abs(sap.tax_sum_by_tax[tax]))
                if diff > eps:
                    messages.append({
                        "tax_symbol_err": tax,
                        "status": Record.STATUS_BAD,
                        "message": Record.MESSAGE_DIFFERENT_TAX_SUM,
                        "comment": comment

                    })

        if len(taxes_in_printer):
            for tax in taxes_in_printer:
                messages.append({
                    "tax_symbol_err": tax,
                    "status": Record.STATUS_BAD,
                    "message": Record.MESSAGE_TAX_ONLY_PRINTER,
                    "comment": comment

                })

        if len(taxes_in_sap):
            for tax in taxes_in_sap:

                # append message when in taxes is technical code
                if sap.TAX_TECHNICAL_CODE in taxes_in_sap:
                    comment = Record.MESSAGE_TECHNICAL_CODE

                # skip, when actual tax is technical code equal 0.0
                if tax == sap.TAX_TECHNICAL_CODE and abs(sap.tax_sum_by_tax[tax]) < eps:
                    continue
                messages.append({
                    "tax_symbol_err": tax,
                    "status": Record.STATUS_BAD,
                    "message": Record.MESSAGE_TAX_ONLY_SAP,
                    "comment": comment
                })

        return messages
