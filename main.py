#!/usr/bin/python
# -*- coding: utf-8 -*-

# ### todo
# check files encodings


import argparse
import report_parser


def main():

    p = report_parser.ReportParser()
    p.args = args
    sap = p.read_sap_report2(args["sap"])
    printer = p.read_printer_report(args["printer"])
    p.compare_write_reports2(printer, sap)
    exit()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Parser raportow z drukarki fiskalnej i systemu SAP."
                                                 " Sprawdza spojnosc danych miedzy tymi raportami, podsumowanie zapisane w csv")
    parser.add_argument('-s', '--sap', default="files/rejest_VAT.txt", help="nazwa pliku z raportem z systemu SAP")
    parser.add_argument('-p', '--printer', default=["files/printer.txt"], nargs="+", help="nazwa pliku z raportem z drukarki fiskalnej") # nargs="+"
    parser.add_argument('-o', '--out', default="output.txt", help="naza wyjsciowego csv", )
    parser.add_argument('-d', '--date', default="", help="miesiac i rok, do zawezenia parsowanych raportow"
                                                         " w formacie MM.RRRR, np. 05.2015", )
    args = vars(parser.parse_args())
    print(args)
    print(args["sap"])
    print(args["printer"])
    print(args["out"])


    main()
