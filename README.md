## Fiscal report parser
Parses csv report exported from SAP and compares with reports from fiscal printers

### Usage
```sh
$ main.py -p printer1 printer2 -s sap -o output -d date
```

Params - all mandatory

```sh
-p - paths to printer sources - one or more files
-s - path to SAP source - one file
-o - output filename
-d - date - MM.YYYY - month and year, parser parses records only for one month. Eg. 04.2015
```

### Help

```sh
$ main.py -h
```
### How prepare parser
1. Check printer report files encodings - have to be UTF-8 (use eg. Notepad++: Encoding > Convert to UTF-8 and save)
2. Check columns mappings for sap file in sap_record.py (constants prefixed by POS_ )
    - first kolumn number = 0
    - easiest way to check - enumerate headers in row above and compare header in sap with comment for each constant
3. Check if date format in sap file fits DATE_FORMAT constant
4. Check csv delimiter (default is \t)

