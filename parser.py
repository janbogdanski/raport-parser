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
    type = ''
    docNo = ''
firstLine = 0
typeExpected = 'RV'
f = open("rejestr")
f = open("rejest_VAT.txt")
rejestr = f.read()
lines = rejestr.splitlines()[firstLine:]
sap = defaultdict(list)
for line in iter(lines):
    try:
        lineValues = line.split("\t")
        typeFound = lineValues[SapRecord.POS_TYPE].strip()
        if typeFound != typeExpected:
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

for item in sap:
    for i in sap[item]:
        print("%s %s" % (i.docNo, i.refNum) )
        # pprint (vars(i))


