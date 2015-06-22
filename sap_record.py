#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'jan.bogdanski'
from record import Record

class SapRecord (Record):

    # columns mappings

    # row with asertisk in POS_TYPE_SUM column, contains sum for all rows for one type
    # should be omitted
    POS_TYPE_SUM = 0
    POS_TYPE = 1
    # POS_DOC_NO = 999

    # DocumentNo in new SAP files
    POS_REF_NO = 3
    POS_DOC_DATE = 5

    # Tx
    POS_TAX_SYMBOL = 15
    POS_TAX_RATE = 16
    POS_GROSS = 17

    # Tax base amount
    POS_NET = 18

    # Output Tax Pay.
    POS_TAX_VAL = 19


    # sap report contains few lines on top, which should be skipped
    FIRST_REPORT_LINE = 8

    TYPE_EXPECTED = ("RV",) # "R1"

    # each type has sum row, which should be skipped
    TYPE_SUM_MARK = "*"

    TAX_TECHNICAL_CODE = "YA"

    # DATE_FORMAT = "%d.%m.%Y"
    DATE_FORMAT = "%Y-%m-%d"
    type = ''
    taxRate = ''
    gross = ''
    net = 0
    taxVal = ''
