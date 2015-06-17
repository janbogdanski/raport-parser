#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'jan.bogdanski'
from record import Record, eps
from sap_record import SapRecord
from printer_record import PrinterRecord
import csv
from collections import defaultdict
import time
import re


class ReportParser (object):
    args = {}
    def read_printer_report(self, files):
        rejestr = ""

        for filename in files:
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
                    if self.args["date"] and time.strftime("%m.%Y", converted_date) == self.args["date"]:
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
            if self.args["date"] and not valid_date:
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

    def read_sap_report2(self, files):

        with open(files, 'r') as f:
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
                        if self.args["date"] and time.strftime("%m.%Y", converted_date) != self.args["date"]:
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

    def compare_write_reports2(self, printer, sap):
        """
        :type printer: list of PrinterRecord
        :type sap: list of SapRecord
        :return:
        """
        f = open(self.args["out"], 'wt')
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
                        # tax_diff = Record.round(abs(abs(printer[refNum].tax_sum_by_tax.get(tax_symbol, 0)) - abs(sap[refNum].tax_sum_by_tax.get(tax_symbol, 0))))
                        tax_diff = Record.round(printer[refNum].tax_sum_by_tax.get(tax_symbol, 0) - abs(sap[refNum].tax_sum_by_tax.get(tax_symbol, 0)))
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