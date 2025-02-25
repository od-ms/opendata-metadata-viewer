import openpyxl
import sys
import csv

# Datei einlesen
excel_file = 'src/data/datensaetze.xlsx'
wb = openpyxl.load_workbook(excel_file)
ws = wb.active

# Zeilen filtern, die in der ersten Spalte einen Wert haben
rows = []
for row in ws.iter_rows(values_only=True):
    if row[0] is not None:
        rows.append(row)

csv_file = sys.stdout
csv_writer = csv.writer(csv_file)
for row in rows:
    csv_writer.writerow(row)

