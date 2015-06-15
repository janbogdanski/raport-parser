#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'jan.bogdanski'
from record import Record

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
