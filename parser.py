#!/usr/bin/python
# -*- coding: utf-8 -*-

# ### todo
# check files encodings
from collections import defaultdict
import re
import csv
import argparse
import time

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
        return round(float(num.replace('.', '').replace(',', '.').replace(' ', '')), 2)

    @staticmethod
    def round(num):
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
        if SapRecord.TAX_TECHNICAL_CODE in taxes_in_sap\
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
                if SapRecord.TAX_TECHNICAL_CODE in taxes_in_sap:
                    comment = Record.MESSAGE_TECHNICAL_CODE

                # skip, when actual tax is technical code equal 0.0
                if tax == SapRecord.TAX_TECHNICAL_CODE and abs(sap.tax_sum_by_tax[tax]) < eps:
                    continue
                messages.append({
                    "tax_symbol_err": tax,
                    "status": Record.STATUS_BAD,
                    "message": Record.MESSAGE_TAX_ONLY_SAP,
                    "comment": comment
                })

        return messages

class SapRecord (Record):

    # columns mappings
    POS_TYPE_SUM = 1
    POS_TYPE = 3
    POS_DOC_NO = 5
    POS_REF_NO = 11
    POS_DOC_DATE = 16
    POS_TAX_SYMBOL = 39
    POS_TAX_RATE = 40
    POS_GROSS = 41
    POS_NET = 42
    POS_TAX_VAL = 43

    #sap report contains few lines on top, which should be skipped
    FIRST_REPORT_LINE = 7

    TYPE_EXPECTED = ("RV",) # "R1"

    # each type has sum row, which should be skipped
    TYPE_SUM_MARK = "*"

    TAX_TECHNICAL_CODE = "YA"

    DATE_FORMAT = "%d.%m.%Y"
    type = ''
    taxRate = ''
    gross = ''
    net = 0
    taxVal = ''

class PrinterRecord (Record):
    # todo czy jest w kazdym raporcie z drukarki??
    # oddziela naglowek drukarki
    HEADER_DELIMITER = "----------------------------------------"

    # oddziela kolejne rachunki
    RECEIPT_DELIMITER = r"\*{40,}"

    # na rachunku oddziela czesc z produktami od czesci z podsumowaniem
    PRODUCTS_SUMMARY_DELIMITER = "- - - - - - - - - - - - - - - - - - - -"
    RECEIPTS_EXCLUDED = ('A N U L O W A N Y', 'B Ł Ą D   I N T E R F E J S U', 'R A P O R T   D O B O W Y', 'R A P O R T   S E R W I S O W Y',
                         'ZEROWANIE RAM', 'PROGRAMOWANIE ZEGARA', 'RAPORT ZEROWANIA RAM', 'PROGRAMOWANIE NAGŁÓWKA', 'RAPORT KONFIGURACJI SPRZĘTU')
    # na pewno jesszcze "STAN KASY", ale ryzykowne

    RECEIPT_DOCUMENT_DATE = "^(\d{4}\-\d{2}\-\d{2})\s+\d+$"
    RECEIPT_SALE_SUM_BY_TAX_REGEX = "^SPRZEDAŻ\s+OPODATK.\s+([A-Z]{1})\s+(\d+,\d+)$"
    RECEIPT_TAX_SUM_BY_TAX_REGEX = "^PTU\s+([A-Z]{1})\s+.*?(\d+,\d+)$"
    RECEIPT_TOTAL_TAX_SUM_REGEX = "^SUMA\s+PTU.*?(\d+,\d+)$"
    RECEIPT_SUM_ROW = "S U M A   P L N"
    RECEIPT_REF_NUM_ROW = "Nr sys."
    RECEIPT_REF_NUM_PREFIX = "DNPL"

    DATE_FORMAT = "%Y-%m-%d" # 2015-04-01

    # PRICE_PATTERN = "(\d+,\d+)([A-Z]{1}|[A-Z]{3})$"

    sum = ''

def read_printer_report():
    rejestr = ""
    for filename in args.printer:
        f = open(filename)
        rejestr += f.read()
    # rejestr.decode('iso-8859-1').encode('utf8')

    # split rejestr to blocks by receipt delimiter
    blocks_read = re.split(PrinterRecord.RECEIPT_DELIMITER, rejestr)

    print "\n\nblocks_read " + str(len(blocks_read)) + "\n\n"

    blocks = []
    printer = defaultdict(list)

    # exclude receipt if contains any string of RECEIPTS_EXCLUDED
    for block in blocks_read:
        if not len(block):
            continue

        # check if block contains one of strings, which excludes that receipt
        invalid_block = [text for index, text in enumerate(PrinterRecord.RECEIPTS_EXCLUDED) if str(text) in block]
        if not any(invalid_block):
            blocks.append(block)

    # 'blocks' contain valid receipts
    for receipt in blocks:

        refNum = None
        prices = []
        sale_sum_by_tax = {}
        tax_sum_by_tax = {}
        total_tax_sum = 0
        valid_date = False

        try:
            # split receipts to products part and summary
            products, summary = receipt.split(PrinterRecord.PRODUCTS_SUMMARY_DELIMITER)
        except ValueError as detail:
            print detail
            print receipt
            print "sprawdz kodowanie pliku (czy utf8) jesli duzo"
            continue

        # parse products part line by line
        for line in products.splitlines():
            # print line

            # data dokumentu, na start valid_date jest false,
            doc_date = re.search(PrinterRecord.RECEIPT_DOCUMENT_DATE, line, re.I)

            if not valid_date and doc_date:
                converted_date = time.strptime(doc_date.group(1), PrinterRecord.DATE_FORMAT)
                if args.date and time.strftime("%m.%Y", converted_date) == args.date:
                    valid_date = True

            # sprawdzenie czy na koncu linii jest cena np. 11,54A
            search = re.search(r"(\d+,\d+)([A-Z]{1})$", line, re.I)
            if search:

                price = float(search.group(1).strip().replace(' ', '').replace(',', '.'))
                prices.append(price)

        # collect data from summary lines, taxes and sums
        for line in summary.splitlines():

            # suma sprzedazy po typie podatku
            sum_tax_type = re.search(PrinterRecord.RECEIPT_SALE_SUM_BY_TAX_REGEX, line, re.I)
            if sum_tax_type:
                sale_sum_by_tax[sum_tax_type.group(1)] = Record.round(sum_tax_type.group(2).strip().replace(' ', '').replace(',', '.'))

            # suma podatku po typie podatku
            tax_type_by_tax = re.search(PrinterRecord.RECEIPT_TAX_SUM_BY_TAX_REGEX, line, re.I)
            if tax_type_by_tax:
                tax_sum_by_tax[tax_type_by_tax.group(1)] = Record.round(tax_type_by_tax.group(2).strip().replace(' ', '').replace(',', '.'))

            # calkowita suma podatku
            tax_total = re.search(PrinterRecord.RECEIPT_TOTAL_TAX_SUM_REGEX, line, re.I)
            if tax_total:
                total_tax_sum = Record.round(tax_total.group(1).strip().replace(' ', '').replace(',', '.'))

            # suma rachunku z wiersza z suma
            if PrinterRecord.RECEIPT_SUM_ROW in line:
                gross_sum = Record.round(line.replace(PrinterRecord.RECEIPT_SUM_ROW, '').strip().replace(' ', '').replace(',', '.'))

            # numer rachunku powiazany z numerem z sap
            if PrinterRecord.RECEIPT_REF_NUM_ROW in line:
                refNum = str(line.replace(PrinterRecord.RECEIPT_REF_NUM_ROW, '')
                             .replace(PrinterRecord.RECEIPT_REF_NUM_PREFIX, '').strip().replace(' ', ''))
        if not refNum:
            # np. testowe wydruki na drukarce
            print 'brak refNum na paragonie'
            # print receipt
            continue
        if args.date and not valid_date:
            print 'data spoza zakresu ' + refNum
            continue

        record = PrinterRecord()
        record.refNum = refNum
        record.sale_sum_by_tax = sale_sum_by_tax
        record.tax_sum_by_tax = tax_sum_by_tax
        record.gross_prices = prices
        record.gross_sum = gross_sum
        record.total_tax_sum = total_tax_sum
        printer[refNum] = record

    return printer

def read_sap_report2():

    with open(args.sap, 'r') as f:
        rejestr = csv.reader(f, delimiter="\t")

        # skip first lines
        [(next(rejestr)) for i in range(0, SapRecord.FIRST_REPORT_LINE)]

        sap = defaultdict(list)
        for line in rejestr:
            try:

                type_found = line[SapRecord.POS_TYPE].strip()
                if type_found in SapRecord.TYPE_EXPECTED:
                    if line[SapRecord.POS_TYPE_SUM].strip() == SapRecord.TYPE_SUM_MARK:

                        # linia z suma wszystkich wpisow dla danego typu
                        continue

                    # check if document date if equal to passed
                    doc_date = str(line[SapRecord.POS_DOC_DATE].strip())
                    converted_date = time.strptime(doc_date, SapRecord.DATE_FORMAT)
                    if args.date and time.strftime("%m.%Y", converted_date) != args.date:
                        continue

                    refNum = str(line[SapRecord.POS_REF_NO].strip())
                    if refNum in sap:
                        record = sap[refNum]
                        """
                        @:type SapRecord
                        """
                        a = 'b'
                    else:
                        record = SapRecord()
                        b = 'fg'

                    # gross = record.gross = abs(record.to_float(lineValues[SapRecord.POS_GROSS].strip()))
                    # gross - wartosc brutto za dany przedmiot
                    gross = SapRecord.to_float(line[SapRecord.POS_GROSS].strip())

                    # stawka podatku, liczbowo
                    # taxRate = SapRecord.to_float(line[SapRecord.POS_TAX_RATE].strip())

                    # net - wartosc netto za dany przedmiot
                    net = SapRecord.to_float(line[SapRecord.POS_NET].strip())

                    # taxVal - wartosc podatku za dany przedmiot
                    taxVal = SapRecord.to_float(line[SapRecord.POS_TAX_VAL].strip())

                    record.type = line[SapRecord.POS_TYPE].strip()

                    total_tax_sum = 0

                    tax_symbol = line[SapRecord.POS_TAX_SYMBOL].strip()
                    if tax_symbol in SapRecord.tax_map:
                        tax_symbol = SapRecord.tax_map[tax_symbol]
                    tax_symbol = SapRecord.tax_map.get(tax_symbol, tax_symbol)

                    record.sale_sum_by_tax[tax_symbol] = Record.round(record.sale_sum_by_tax.get(tax_symbol, 0) + gross)
                    record.tax_sum_by_tax[tax_symbol] = Record.round(record.tax_sum_by_tax.get(tax_symbol, 0) + taxVal)
                    record.total_tax_sum = Record.round(record.total_tax_sum + taxVal)
                    record.gross_prices.append(gross)
                    record.gross_sum += gross
                    record.net += net

                    # print(refNum)
                    sap[refNum] = record

                    # pprint (vars(record))
            except ValueError as detail:
                print detail
                print line
            except IndexError as detail:
                print detail
                print line
    return sap

def compare_write_reports2(printer, sap):
    """
    :type printer: list of PrinterRecord
    :type sap: list of SapRecord
    :return:
    """
    f = open(args.out, 'wt')
    output = csv.writer(f)
    output.writerow(('id', 'status', 'message', 'comment', 'tax code diff', 'tax diff', 'taxes by tax', 'tax sum'))

    printer_keys = set(printer.keys())
    sap_keys = set(sap.keys())
    both = printer_keys.intersection(sap_keys)

    only_printer = printer_keys - sap_keys
    only_sap = sap_keys - printer_keys
    tax_diff_by_tax = {}

    for refNum in only_printer:
        for tax in printer[refNum].tax_sum_by_tax:
            output.writerow((refNum, Record.STATUS_BAD, Record.MESSAGE_ONLY_PRINTER, None,
                             tax, printer[refNum].tax_sum_by_tax[tax], printer[refNum].tax_sum_by_tax, printer[refNum].total_tax_sum))
    for refNum in only_sap:
        for tax in sap[refNum].tax_sum_by_tax:

            if tax == SapRecord.TAX_TECHNICAL_CODE and abs(sap[refNum].tax_sum_by_tax[tax]) < eps:
                # skip when contains technical code and tax
                continue
            output.writerow((refNum, Record.STATUS_BAD, Record.MESSAGE_ONLY_SAP, None,
                             tax, abs(sap[refNum].tax_sum_by_tax[tax]), sap[refNum].tax_sum_by_tax, sap[refNum].total_tax_sum))

    for refNum in both:
        messages = Record.equal_records(printer[refNum], sap[refNum])
        if len(messages):
            for message in messages:
                tax_symbol = message["tax_symbol_err"]

                # liczenie sumy roznic podatkow
                tax_diff = None
                if tax_symbol:
                    tax_diff = Record.round(abs(abs(printer[refNum].tax_sum_by_tax.get(tax_symbol, 0)) - abs(sap[refNum].tax_sum_by_tax.get(tax_symbol, 0))))
                    tax_sum = tax_diff_by_tax.get(tax_symbol, 0) + tax_diff
                    tax_diff_by_tax[tax_symbol] = tax_sum

                output.writerow((refNum, message["status"], message["message"], message["comment"], tax_symbol, tax_diff,
                                 (printer[refNum].tax_sum_by_tax, sap[refNum].tax_sum_by_tax),
                                 (printer[refNum].total_tax_sum, sap[refNum].total_tax_sum)))

        else:
            b = 'blad?'

    for tax in tax_diff_by_tax:
        output.writerow((tax, Record.round(tax_diff_by_tax[tax])))

    print '\nliczba wspolnych - ' + str(len(both))
    print 'liczba na drukarce - ' + str(len(only_printer))
    print 'liczba w sap - ' + str(len(only_sap))

def main():

    sap = read_sap_report2()
    printer = read_printer_report()
    compare_write_reports2(printer, sap)
    exit()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Parser raportow z drukarki fiskalnej i systemu SAP."
                                                 " Sprawdza spojnosc danych miedzy tymi raportami, podsumowanie zapisane w csv")
    parser.add_argument('-s', '--sap', default="rejest_VAT.txt", help="nazwa pliku z raportem z systemu SAP")
    parser.add_argument('-p', '--printer', default="printer.txt", nargs="+", help="nazwa pliku z raportem z drukarki fiskalnej") # nargs="+"
    parser.add_argument('-o', '--out', default="output.txt", help="naza wyjsciowego csv", )
    parser.add_argument('-d', '--date', default="", help="miesiac i rok, do zawezenia parsowanych raportow"
                                                         " w formacie MM.RRRR, np. 05.2015", )
    args = parser.parse_args()
    print(args)
    print(args.sap)
    print(args.printer)
    print(args.out)

    main()
