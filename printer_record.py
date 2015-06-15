#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'jan.bogdanski'
from record import Record


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
