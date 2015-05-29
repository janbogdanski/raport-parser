#!/usr/bin/python
# -*- coding: utf-8 -*-

# ### todo
# check files encodings
# zawezanie dla podanych dat - w zrzutach moga byc dane z szerszych okresow
from collections import defaultdict
from pprint import pprint
import re
import csv
import sys
import argparse

eps = 0.000001


class Record (object):
    refNum = ''
    date1 = ''
    date2 = ''
    date3 = ''

    # suma sprzedazy na rachunku po typie podatku
    sale_sum_by_tax = {}

    # suma podatku od sprzedazy, po typie podatku
    tax_sum_by_tax = {}

    # calkowita suma podatku na rachunku
    total_tax_sum = 0
    gross_sum = 0
    gross_prices = []

    STATUS_OK = 'OK'
    STATUS_BAD = 'BAD'

    MESSAGE_ALL_OK = "Zgodne wartosci podatkow "
    MESSAGE_TECHNICAL_CODE = "Technical code w zrzucie"
    MESSAGE_DIFFERENT_TAX_SUM = "Rozne kwoty podatku"
    MESSAGE_TAX_ONLY_PRINTER = "Podatek na rachunku tylko na drukarce"
    MESSAGE_TAX_ONLY_SAP = "Podatek na rachunku tylko wa SAP"
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
        self.sale_sum_by_tax = {}
        self.tax_sum_by_tax = {}
        self.total_tax_sum = 0
        self.gross_sum = 0
        self.gross_prices = []

    # def __eq__(self, other):
    #     print self.
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
        len_prices = len(printer.gross_prices), len(sap.gross_prices)
        gross_sums = (printer.gross_sum, sap.gross_sum, abs(printer.gross_sum) - abs(sap.gross_sum))
        r = (len_prices, gross_sums, cmp(printer.sale_sum_by_tax, sap.sale_sum_by_tax))


        if not len(messages):
            a = 'g'
        return messages

        sum_gross = sum(sap.gross_prices)

        # if len(printer.gross_prices) != len(sap.gross_prices):
        #     a = 'n'
        # return (1,1)
        printer.sort()
        receipt2.sort()

        abs_receipt1 = map(abs, receipt1)
        abs_receipt2 = map(abs, receipt2)
        abs_sum_diff = sum(abs_receipt1) - sum(abs_receipt2)
        # print len(receipt1) == len(receipt2)

        # sap moze miec rekordy ujemne (odpowiadajace sprzedazy na rachunku)
        # i dodatni, bedace korektą

        # sprawdzenie czy dlugosc list (liczba produktow) oraz ich suma jest rowna
        if (len(receipt1) == len(receipt2)) and (abs_sum_diff < eps ):
            # 100% equal
            # print(receipt1, receipt2)
            # exit()
            return True, 'zgodna liczba produktow i suma ich cen w obu raportach'

        # czy absolutne sumy sa rowne
        if (abs(sum(receipt1)) - abs(sum(receipt2))) < eps:
            # print receipt1, receipt2, (abs(sum(receipt1)) - abs(sum(receipt2))) < eps
            #rozna ilosc elementow, ale suma rowna - np. korekty
            return True, 'rozna liczba produktow, zgodna suma cen w obu raportach'
        else:
            return False, 'rozne dane w obu raportach'

        # for record1 in receipt1:
        #     for record2 in receipt2:
        #         print 1

                # if abs(record1['gross'] - record2['gross']) == 0:
                #     print 1
                    # pprint(vars(record1))
                    # pprint(vars(record2))
        # exit()
        # exit()
        # if len(receipt1) == passed:
        #     return True
        # else:
        #     return False





class SapRecord (Record):
    POS_TYPE = 3
    POS_DOC_NO = 5
    POS_REF_NO = 11
    POS_TAX_SYMBOL = 39
    POS_TAX_RATE = 40
    POS_GROSS = 41
    POS_NET = 42
    POS_TAX_VAL = 43
    TYPE_EXPECTED = ("RV",) # "R1"

    TAX_TECHNICAL_CODE = "YA"
    type = ''
    docNo = ''
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
    PRODUCTS_SUMMARY_DELIMITER = "- - - - - - - - - - - - - - - - - - - - "
    RECEIPTS_EXCLUDED = ('A N U L O W A N Y', 'B Ł Ą D   I N T E R F E J S U', 'R A P O R T   D O B O W Y', 'R A P O R T   S E R W I S O W Y')


    RECEIPT_SALE_SUM_BY_TAX_REGEX = "^SPRZEDAŻ\s+OPODATK.\s+([A-Z]{1})\s+(\d+,\d+)$"
    RECEIPT_TAX_SUM_BY_TAX_REGEX = "^PTU\s+([A-Z]{1})\s+.*?(\d+,\d+)$"
    RECEIPT_TOTAL_TAX_SUM_REGEX = "^SUMA\s+PTU.*?(\d+,\d+)$"
    RECEIPT_SUM_ROW = "S U M A   P L N"
    RECEIPT_REF_NUM_ROW = "Nr sys."
    RECEIPT_REF_NUM_PREFIX = "DNPL"

    # PRICE_PATTERN = "(\d+,\d+)([A-Z]{1}|[A-Z]{3})$"

    sum = ''



def read_printer_report():
    uniqe = 0
    f = open(args.printer)
    rejestr = f.read()
    blocks_read = re.split(PrinterRecord.RECEIPT_DELIMITER, rejestr)
    blocks = []
    printer = defaultdict(list)
    ret = defaultdict(list)

    # exclude receipt if contains any string of RECEIPTS_EXCLUDED
    for block in blocks_read:
        if not len(block):
            continue

        invalid_block = [text for index, text in enumerate(PrinterRecord.RECEIPTS_EXCLUDED) if str(text) in block]
        if not any(invalid_block):
            blocks.append(block)

    # 'blocks' contain valid receipts
    for receipt in blocks:

        prices = []
        sale_sum_by_tax = {}
        tax_sum_by_tax = {}
        total_tax_sum = 0
        try:

            products, summary = receipt.split(PrinterRecord.PRODUCTS_SUMMARY_DELIMITER)
        except ValueError as detail:
            print detail

        for line in products.splitlines():
            # print line

            # sprawdzenie czy na koncu linii jest cena np. 11,54A
            # search = re.search(r"(\d+,\d+)([A-Z]{1}|[A-Z]{3})$", line, re.I) # 1 lub 3 znaki - w sumie 3 nie powinno byc
            search = re.search(r"(\d+,\d+)([A-Z]{1})$", line, re.I)
            if search:

                price = float(search.group(1).strip().replace(' ', '').replace(',', '.'))
                prices.append(price)

        # collect data from lines
        for line in summary.splitlines():

            # suma sprzedazy po typie podatku
            sum_tax_type = re.search(PrinterRecord.RECEIPT_SALE_SUM_BY_TAX_REGEX, line, re.I)
            if sum_tax_type:
                sale_sum_by_tax[sum_tax_type.group(1)] = Record.round(sum_tax_type.group(2).strip().replace(' ', '').replace(',', '.'))

            # suma podatku po typie podatku
            tax_type_by_tax = re.search(PrinterRecord.RECEIPT_TAX_SUM_BY_TAX_REGEX, line, re.I)
            if tax_type_by_tax:
                a = Record.round(tax_type_by_tax.group(2).strip().replace(' ', '').replace(',', '.'))
                tax_sum_by_tax[tax_type_by_tax.group(1)] = Record.round(tax_type_by_tax.group(2).strip().replace(' ', '').replace(',', '.'))
                tax_sum_by_tax[tax_type_by_tax.group(1)] = Record.round(tax_type_by_tax.group(2).strip().replace(' ', '').replace(',', '.'))

            # calkowita suma podatku+
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
        # print prices
        compare_sum = 0
        compare = []
        # p = []
        record = PrinterRecord()
        record.refNum = refNum
        record.sale_sum_by_tax = sale_sum_by_tax
        record.tax_sum_by_tax = tax_sum_by_tax
        record.gross_prices = prices
        record.gross_sum = gross_sum
        record.total_tax_sum = total_tax_sum
        printer[refNum] = record

        for price in prices:


            # compare_sum += price
            # compare.append(compare_sum)
            # p.append(price)

            ret[refNum].append(price)

        # if abs(round(compareSum,2) - sum) > 0:
            # print [round(compareSum,2), abs(round(compareSum,2) - sum)]
            # print [compareSum - sum, compareSum, sum]

    # return printer
    return printer

def read_sap_report2():
    first_line = 7
    with open(args.sap, 'r') as f:
        rejestr = csv.reader(f, delimiter="\t")
        [(next(rejestr)) for i in range(0, first_line)]

        sap = defaultdict(list)
        ret = defaultdict(list)
        test = defaultdict(list)
        test2 = defaultdict(list)
        for line in rejestr:
            try:

                type_found = line[SapRecord.POS_TYPE].strip()
                if type_found in SapRecord.TYPE_EXPECTED:
                    a = SapRecord()

                    # invalid type

                    # continue
                    # print lineValues
                    refNum = str(line[SapRecord.POS_REF_NO].strip())
                    if refNum in test2:
                        record = test2[refNum]
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
                    taxRate = SapRecord.to_float(line[SapRecord.POS_TAX_RATE].strip())

                    # net - wartosc netto za dany przedmiot
                    net = SapRecord.to_float(line[SapRecord.POS_NET].strip())

                    # taxVal - wartosc podatku za dany przedmiot
                    taxVal = SapRecord.to_float(line[SapRecord.POS_TAX_VAL].strip())

                    record.type = line[SapRecord.POS_TYPE].strip()
                    # record.docNo =  str(lineValues[SapRecord.POS_DOC_NO].strip())
                    # record.taxRate = abs(record.to_float(lineValues[SapRecord.POS_TAX_RATE].strip()))
                    # record.net = abs(record.to_float(lineValues[SapRecord.POS_NET].strip()))
                    # record.taxVal = abs(record.to_float(lineValues[SapRecord.POS_TAX_VAL].strip()))

                    # prices = []
                    # sale_sum_by_tax = {}
                    # tax_sum_by_tax = {}
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
                    sap[refNum].append(record)
                    rec = {}
                    # rec['refNum'] = record.refNum
                    rec['gross'] = gross
                    ret[refNum].append(gross)
                    test2[refNum] = record
                    test[refNum].append(record)

                    # pprint (vars(record))
            except ValueError as detail:
                print detail
                print line
            except IndexError as detail:
                print detail
                print line
    # return sap

    return test2

def read_sap_report():
    first_line = 10
    f = open(args.sap)
    rejestr = f.read()
    lines = rejestr.splitlines()[first_line:]
    sap = defaultdict(list)
    ret = defaultdict(list)
    for line in iter(lines):
        try:
            line_values = line.split("\t")
            typeFound = line_values[SapRecord.POS_TYPE].strip()
            if typeFound != SapRecord.TYPE_EXPECTED:
                # invalid type
                continue

            # print lineValues
            record = SapRecord()
            refNum = record.refNum = str(line_values[SapRecord.POS_REF_NO].strip())
            # gross = record.gross = abs(record.to_float(lineValues[SapRecord.POS_GROSS].strip()))
            gross = record.gross = record.to_float(line_values[SapRecord.POS_GROSS].strip())

            # record.type = lineValues[SapRecord.POS_TYPE].strip()
            # record.docNo =  str(lineValues[SapRecord.POS_DOC_NO].strip())
            # record.taxRate = abs(record.to_float(lineValues[SapRecord.POS_TAX_RATE].strip()))
            # record.net = abs(record.to_float(lineValues[SapRecord.POS_NET].strip()))
            # record.taxVal = abs(record.to_float(lineValues[SapRecord.POS_TAX_VAL].strip()))

            # print(refNum)
            sap[refNum].append(record)
            rec = {}
            # rec['refNum'] = record.refNum
            rec['gross'] = gross
            ret[refNum].append(gross)

            # pprint (vars(record))
        except ValueError as detail:
            print detail
            print line
        except IndexError as detail:
            print detail
            print line
    # return sap
    return ret

def compare_write_reports(report1, report2):
    f = open(args.out, 'wt')
    output = csv.writer(f)

    out = {}
    r1_keys = set(report1.keys())
    r2_keys = set(report2.keys())
    both = r1_keys.intersection(r2_keys)
    print  both

    only_r1 = r1_keys - r2_keys
    only_r2 = r2_keys - r1_keys
    # modified = {o : (report1[o], report2[o]) for o in both if cmp(report1[o], report2[o])}
    # print(modified)
    # same = set(o for o in intersect_keys if report1[o] == report2[o])
    ok = 0
    bad = 0
    # parse records, where ids are in both dicts

    # equal = [o for o in both for r1 in report1[o] for r2 in report2[o] if abs(r1.gross -  r2.gross) == 0]

    for refNum in only_r1:
        output.writerow((refNum, Record.STATUS_BAD, 'tylko w r1', report1[refNum] ))
    for refNum in only_r2:
        output.writerow((refNum, Record.STATUS_BAD, 'tylko w r2', report2[refNum]))

    for refNum in both:
        # if refNum != '1000003483':
        #     continue
        # print(refNum)
        eq, msg = Record.equal_records(report1[refNum], report2[refNum])
        print(msg)
        if eq:
            output.writerow((refNum, Record.STATUS_OK, msg, (report1[refNum], report2[refNum])))
            ok += 1
            # print report1[refNum], report2[refNum]

            # print refNum
        else:
            output.writerow((refNum, Record.STATUS_BAD , msg, (report1[refNum], report2[refNum])))
            # print(refNum)
            # print(cmp(report1[refNum], report2[refNum]))
            # print report1[refNum], report2[refNum]
            bad += 1
        # exit()
    # pprint(equal)
    # print len(both), len(equal), ok, bad

    # print equal

    # for refNum in only_r1:
        #print None

    # for refNum in only_r1:
     # print refNum

    # parse record which are
    # for item in report1:
    pprint (len(both))
    # pprint (only_r1)
    pprint (len(only_r1))
    # pprint (only_r2)
    # pprint (same)

def compare_write_reports2(printer, sap):
    """

    :type printer: list of PrinterRecord
    :type sap: list of SapRecord
    :return:
    """
    f = open(args.out, 'wt')
    output = csv.writer(f)
    output.writerow(('id', 'status', 'message', 'comment', 'tax code diff', 'tax diff', 'taxes by tax', 'tax sum'))

    out = {}
    r1_keys = set(printer.keys())
    r2_keys = set(sap.keys())
    both = r1_keys.intersection(r2_keys)

    only_r1 = r1_keys - r2_keys
    only_r2 = r2_keys - r1_keys
    # modified = {o : (printer[o], sap[o]) for o in both if cmp(printer[o], sap[o])}
    # print(modified)
    # same = set(o for o in intersect_keys if printer[o] == sap[o])
    c = len(r1_keys), len(r2_keys), len(both)
    ok = 0
    bad = 0
    tax_diff_by_tax = {}

    # parse records, where ids are in both dicts

    # equal = [o for o in both for r1 in printer[o] for r2 in sap[o] if abs(r1.gross -  r2.gross) == 0]

    for refNum in only_r1:
        output.writerow((refNum, Record.STATUS_BAD, Record.MESSAGE_ONLY_PRINTER, None, None, None, printer[refNum].sale_sum_by_tax))
    for refNum in only_r2:
        output.writerow((refNum, Record.STATUS_BAD, Record.MESSAGE_ONLY_SAP, None, None, None, sap[refNum].sale_sum_by_tax))

    for refNum in both:
        # if refNum != '1000003483':
        #     continue
        # print(refNum)
        messages = Record.equal_records(printer[refNum], sap[refNum])
        if len(messages):
            a = 'd'
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
        # msg = 'a'
        # eq = '1'
        # print(msg)
        # if eq:
        #     output.writerow((refNum, Record.STATUS_OK, msg, (printer[refNum], sap[refNum])))
        #     ok += 1
            # print printer[refNum], sap[refNum]

            # print refNum
        # else:
        #     output.writerow((refNum, Record.STATUS_BAD , msg, (printer[refNum], sap[refNum])))
            # print(refNum)
            # print(cmp(printer[refNum], sap[refNum]))
            # print printer[refNum], sap[refNum]
            # bad += 1
        # exit()
    # pprint(equal)
    # print len(both), len(equal), ok, bad

    # print equal

    # for refNum in only_r1:
        #print None

    # for refNum in only_r1:
     # print refNum

    # parse record which are
    # for item in report1:
    pprint (len(both))
    # pprint (only_r1)
    pprint (len(only_r1))
    # pprint (only_r2)
    # pprint (same)

def eq_records(printer, sap):
    """

    :type printer: PrinterRecord
    :type sap: SapRecord
    :return:
    """

    return
def main():

    sap = read_sap_report2()
    printer = read_printer_report()
    a = sap['1000000016']

    # print sap
    # print printer

    test1 = sap['1000003334']
    test2 = printer['1000003334']
    pprint((test1, test2))
    print cmp(test1, test2)

    compare_write_reports2(printer, sap)

    exit()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Parser raportow z drukarki fiskalnej i systemu SAP."
                                                 " Sprawdza spojnosc danych miedzy tymi raportami, podsumowanie zapisane w csv")
    parser.add_argument('-s', '--sap', default="rejest_VAT.txt", help="nazwa pliku z raportem z systemu SAP")
    parser.add_argument('-p', '--printer', default="printer.txt", help="nazwa pliku z raportem z drukarki fiskalnej") # nargs="+"
    parser.add_argument('-o', '--out', default="output.txt", help="naza wyjsciowego csv", )
    args = parser.parse_args()
    print(args)
    print(args.sap)
    print(args.printer)
    print(args.out)

    main()
