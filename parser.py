#!/usr/bin/python
# -*- coding: utf-8 -*-

#### todo
#check files encodings
from collections import defaultdict
from pprint import pprint




class Record:
    refNum = ''
    date1 = ''
    date2 = ''
    date3 = ''
    taxRate = ''
    gross = ''
    net = ''
    taxVal = ''

    @staticmethod
    def toFloat(num):
        return float(num.replace('.','').replace(',','.').replace(' ',''))



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
    RECEIPT_DELIMITER = "****************************************"
    RECEIPTS_EXCLUDED = ('A N U L O W A N Y', 'B Ł Ą D   I N T E R F E J S U', 'R A P O R T   D O B O W Y')

def read_printer_raport():
    uniqe = 0
    f = open("printer.txt")
    rejestr = f.read()
    blocksRead = rejestr.split(PrinterRecord.RECEIPT_DELIMITER)
    blocks = []


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

def read_sap_raport():
    firstLine = 0
    f = open("rejest_VAT.txt")
    rejestr = f.read()
    lines = rejestr.splitlines()[firstLine:]
    sap = defaultdict(list)
    for line in iter(lines):
        try:
            lineValues = line.split("\t")
            typeFound = lineValues[SapRecord.POS_TYPE].strip()
            if typeFound != SapRecord.TYPE_EXPECTED:
                #invalid type
                continue

            # print lineValues
            record = SapRecord()
            record.type = lineValues[SapRecord.POS_TYPE].strip()
            record.docNo =  int(lineValues[SapRecord.POS_DOC_NO].strip())
            refNum = record.refNum = int(lineValues[SapRecord.POS_REF_NO].strip())

            record.taxRate = record.toFloat(lineValues[SapRecord.POS_TAX_RATE].strip())

            # record.taxRate = float(lineValues[SapRecord.POS_TAX_RATE].strip().replace(',','.'))
            record.gross = record.toFloat(lineValues[SapRecord.POS_GROSS].strip())
            record.net = record.toFloat(lineValues[SapRecord.POS_NET].strip())
            record.taxVal = record.toFloat(lineValues[SapRecord.POS_TAX_VAL].strip())

            # print(refNum)
            sap[refNum].append(record)

            # pprint (vars(record))
        except ValueError as detail:
            print detail
        except IndexError as detail:
            print detail
    return sap

#sap = read_sap_raport()
sap = read_printer_raport()
exit()
for item in sap:
    for i in sap[item]:
        print("%s %s" % (i.docNo, i.refNum) )
        # pprint (vars(i))


