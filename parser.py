#!/usr/bin/python
# -*- coding: utf-8 -*-

#### todo
#check files encodings
from collections import defaultdict
from pprint import pprint
import re
import csv

eps = 0.000001


class Record:
    refNum = ''
    date1 = ''
    date2 = ''
    date3 = ''
    taxRate = ''
    gross = ''
    net = ''
    taxVal = ''
    STATUS_OK = 'OK'
    STATUS_BAD = 'BAD'

    # def __eq__(self, other):
    #     print self.
    @staticmethod
    def toFloat(num):
        return round(float(num.replace('.','').replace(',','.').replace(' ','')),2)

    @staticmethod
    def equalRecords(receipt1, receipt2):
        passed = 0
        receipt1.sort()
        receipt2.sort()

        absReceipt1 = map(abs, receipt1)
        absReceipt2 = map(abs, receipt2)
        absSumDiff  = sum(absReceipt1) - sum(absReceipt2)
        # print len(receipt1) == len(receipt2)

        #sap moze miec rekordy ujemne (odpowiadajace sprzedazy na rachunku)
        #i dodatni, bedace korektą

        #sprawdzenie czy dlugosc list (liczba produktow) oraz ich suma jest rowna
        if (len(receipt1) == len(receipt2)) and (absSumDiff < eps ):
            #100% equal
            # print(receipt1, receipt2)
            # exit()
            return (True, 'zgodna liczba produktow i suma ich cen w obu raportach')

        #czy absolutne sumy sa rowne
        if ((abs(sum(receipt1)) - abs(sum(receipt2))) < eps):
            # print receipt1, receipt2, (abs(sum(receipt1)) - abs(sum(receipt2))) < eps
            #rozna ilosc elementow, ale suma rowna - np. korekty
            return (True, 'rozna liczba produktow, zgodna suma cen w obu raportach')
        else:
            return (False, 'rozne dane w obu raportach')

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
    POS_REF_NO = 7
    POS_TAX_RATE = 31
    POS_GROSS = 32
    POS_NET = 33
    POS_TAX_VAL = 34
    TYPE_EXPECTED = "RV"
    type = ''
    docNo = ''

class PrinterRecord (Record):
    #todo czy jest w kazdym raporcie z drukarki??
    #oddziela naglowek drukarki
    HEADER_DELIMITER = "----------------------------------------"

    #oddziela kolejne rachunki
    RECEIPT_DELIMITER = "****************************************"

    #na rachunku oddziela czesc z produktami od czesci z podsumowaniem
    PRODUCTS_SUMMARY_DELIMITER = "- - - - - - - - - - - - - - - - - - - - "
    RECEIPTS_EXCLUDED = ('A N U L O W A N Y', 'B Ł Ą D   I N T E R F E J S U', 'R A P O R T   D O B O W Y')

    RECEIPT_SUM_ROW = "S U M A   P L N"
    RECEIPT_REF_NUM_ROW = "Nr sys."
    RECEIPT_REF_NUM_PREFIX = "DNPL"

    #PRICE_PATTERN = "(\d+,\d+)([A-Z]{1}|[A-Z]{3})$"

    sum = ''

def read_printer_raport():
    uniqe = 0
    f = open("printer.txt")
    rejestr = f.read()
    blocksRead = rejestr.split(PrinterRecord.RECEIPT_DELIMITER)
    blocks = []
    printer = defaultdict(list)
    ret = defaultdict(list)


    for block in blocksRead:
        if(not len(block)):
            continue


        #for index, text in enumerate(PrinterRecord.RECEIPTS_EXCLUDED):
        #    if str(text) not in block:
        #        print text
        #        blocks.append(block)


        #validateBlock =(text for index, text in enumerate(PrinterRecord.RECEIPTS_EXCLUDED) if str(text) not in block)
        invalidBlock = [text for index, text in enumerate(PrinterRecord.RECEIPTS_EXCLUDED) if str(text) in block]
        if (not any(invalidBlock)):
            blocks.append(block)


    #blocks contain valid receipts
    for receipt in blocks:

        prices = []
        try:

            products, summary = receipt.split(PrinterRecord.PRODUCTS_SUMMARY_DELIMITER)
        except ValueError as detail:
            print detail

        for line in products.splitlines():
            #print line
            search = re.search(r"(\d+,\d+)([A-Z]{1}|[A-Z]{3})$", line, re.I)
            if search:

                price = float(search.group(1).strip().replace(' ', '').replace(',', '.'))
                prices.append(price)



        for line in summary.splitlines():

            if PrinterRecord.RECEIPT_SUM_ROW in line:
                sum = float(line.replace(PrinterRecord.RECEIPT_SUM_ROW, '').strip().replace(' ', '').replace(',', '.'))


            if PrinterRecord.RECEIPT_REF_NUM_ROW in line:
                 refNum =  str(line.replace(PrinterRecord.RECEIPT_REF_NUM_ROW, '').replace(PrinterRecord.RECEIPT_REF_NUM_PREFIX, '').strip().replace(' ', ''))
        #print prices
        compareSum = 0
        compare = []
        p = []
        for price in prices:
            rec = {}
            rec['gross'] = price
            # rec['refNum'] = refNum

            record = PrinterRecord()
            record.gross = price
            record.refNum = refNum


            #record.sum = sum

            compareSum += price
            compare.append(compareSum)
            p.append(price)

            printer[refNum].append(record)
            ret[refNum].append(price)



        # if abs(round(compareSum,2) - sum) > 0:
            # print [round(compareSum,2), abs(round(compareSum,2) - sum)]
            # print [compareSum - sum, compareSum, sum]
            # print compare
            # print p

            #pprint(vars(record))
    # return printer
    return ret


def read_sap_raport():
    firstLine = 10
    f = open("rejest_VAT.txt")
    rejestr = f.read()
    lines = rejestr.splitlines()[firstLine:]
    sap = defaultdict(list)
    ret = defaultdict(list)
    for line in iter(lines):
        try:
            lineValues = line.split("\t")
            typeFound = lineValues[SapRecord.POS_TYPE].strip()
            if typeFound != SapRecord.TYPE_EXPECTED:
                #invalid type
                continue

            # print lineValues
            record = SapRecord()
            refNum = record.refNum = str(lineValues[SapRecord.POS_REF_NO].strip())
            # gross = record.gross = abs(record.toFloat(lineValues[SapRecord.POS_GROSS].strip()))
            gross = record.gross = record.toFloat(lineValues[SapRecord.POS_GROSS].strip())

            #record.type = lineValues[SapRecord.POS_TYPE].strip()
            #record.docNo =  str(lineValues[SapRecord.POS_DOC_NO].strip())
            #record.taxRate = abs(record.toFloat(lineValues[SapRecord.POS_TAX_RATE].strip()))
            #record.net = abs(record.toFloat(lineValues[SapRecord.POS_NET].strip()))
            #record.taxVal = abs(record.toFloat(lineValues[SapRecord.POS_TAX_VAL].strip()))

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

def compare_reports(report1, report2):
    out = {}
    r1_keys = set(report1.keys())
    r2_keys = set(report2.keys())
    both = r1_keys.intersection(r2_keys)
    print  both


    only_r1 = r1_keys - r2_keys
    only_r2 = r2_keys - r1_keys
    # modified = {o : (report1[o], report2[o]) for o in both if cmp(report1[o], report2[o])}
    # print(modified)
    #same = set(o for o in intersect_keys if report1[o] == report2[o])
    ok = 0
    bad = 0
    #parse records, where ids are in both dicts

    #equal = [o for o in both for r1 in report1[o] for r2 in report2[o] if abs(r1.gross -  r2.gross) == 0]

    for refNum in only_r1:
        output.writerow((refNum, Record.STATUS_BAD, 'tylko w r1', report1[refNum] ))
    for refNum in only_r2:
        output.writerow((refNum, Record.STATUS_BAD, 'tylko w r2', report2[refNum]))

    for refNum in both:
        # if refNum != '1000003483':
        #     continue
        # print(refNum)
        eq, msg = Record.equalRecords(report1[refNum], report2[refNum])
        print(msg)
        if eq:
            output.writerow((refNum, Record.STATUS_OK, msg, (report1[refNum], report2[refNum])))
            ok += 1
            # print report1[refNum], report2[refNum]

            #print refNum
        else:
            output.writerow((refNum, Record.STATUS_BAD , msg, (report1[refNum], report2[refNum])))
            # print(refNum)
            # print(cmp(report1[refNum], report2[refNum]))
            # print report1[refNum], report2[refNum]
            bad += 1
        #exit()
    # pprint(equal)
    # print len(both), len(equal), ok, bad

    #print equal

    #for refNum in only_r1:
        #print None

    #for refNum in only_r1:
     #   print refNum

    #parse record which are
    #for item in raport1:
    pprint (len(both))
    #pprint (only_r1)
    pprint (len(only_r1))
    #pprint (only_r2)
    #pprint (same)
f = open('output.txt', 'wt')
output = csv.writer(f)
sap = read_sap_raport()
printer = read_printer_raport()

print sap
print printer

test1 = sap['1000003334']
test2 = printer['1000003334']
pprint((test1, test2))
print cmp(test1,test2)



compare_reports(printer, sap)

exit()
for item in sap:
    for i in sap[item]:
        print("%s %s" % (i.refNum, '') )
        pprint (vars(i))


