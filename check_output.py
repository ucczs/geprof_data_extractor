import csv
import copy

g_file_name = 'output_v04.csv'
# g_file_name = 'output_v04_small.csv'
g_allData = []

g_numbers_only_data = [
    'Artikel-Nummer:',
    'Größe:',
    'Inhalt (Liter):',
    'Gewicht (kg):',
    'Mengeneinheit Nr:',
    'Mengeneinheit Pal:',
    'Mengeneinheit Lage:',
    'Produzent-Nr:',
    'Leergut-Nummer:',
    'Pfand (€):',
    'MwSt-Satz (%):',
    'Preislisten-Nummer:',
    'Meldebestand:',
    'Höchstbestand:',
    'GTIN Flasche:',
    'GTIN Kiste / Faß:',
    'GTIN Palette:',
    'Listenpreis/Grundpreis:',
    'Listenpreis/Grundpreis Fl:',
    'Einkaufspreis xx:',
    'Einkaufspreis xx Fl:',
    'Preis yy:',
    'Preis yy Fl:',
    'zz. Lieferanten-Konditionen Wert',
]


g_defined_data_type_only = [
    'MwSt-Satz (%):',
    'Pfand (€):',
    'Rückvergütung:',
    'Rabattartikel:',
    'Preisliste:',
    'Aktiv:',
    'Listenpreis/Grundpreis Kommentar:',
    'zz. Lieferanten-Konditionen Kondi-Gültigkeit',
    'zz. Lieferanten-Konditionen Auf-/Abschlag',
    'zz. Lieferanten-Konditionen Einheit',
    'zz. Lieferanten-Konditionen Geltungsbereich'
]

g_found_data_in_defined_data_type = {}


def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False


# xx = for Einkaufspreis -> 1 - 3
# yy = for Preis -> 1 - 9
# zz = Lieferanten-Konditionen -> 1 - 50
def replace_variable_in_list(input_list):
    for element in reversed(input_list):
        # Einkaufspreis
        if element.find("xx") >= 0:
            input_list.remove(element)
            for i in range(1,4):
                input_list.append(element.replace('xx', str(i)))
        
        # Preis
        elif element.find("yy") >= 0:
            input_list.remove(element)
            for i in range(1,10):
                input_list.append(element.replace('yy', str(i)))
        
        # Lieferanten-Konditionen
        elif element.find("zz") >= 0:
            input_list.remove(element)
            for i in range(1,51):
                input_list.append(element.replace('zz', str(i)))

    return input_list


def check_for_expected_data():
    global g_defined_data_type_only
    global g_allData
    global g_found_data_in_defined_data_type

    g_defined_data_type_only = replace_variable_in_list(g_defined_data_type_only)

    for expected_data_type in g_defined_data_type_only:
        temp_list = []
        for article in g_allData:
            temp_list.append(article[expected_data_type])

        g_found_data_in_defined_data_type[expected_data_type] = set(temp_list)

        print("data Type: ")
        print(expected_data_type)
        print(g_found_data_in_defined_data_type[expected_data_type])
        print(30*'*')


def check_for_numbers_only():
    global g_numbers_only_data
    global g_allData

    g_numbers_only_data = replace_variable_in_list(g_numbers_only_data)

    number_errors = 0

    for article in g_allData:
        for numbers_data in g_numbers_only_data:
            if article[numbers_data] == None or isfloat(article[numbers_data]) or article[numbers_data] == "":
                pass
            else:
                print(numbers_data)
                print(article[numbers_data])
                print(20*'_')
                number_errors += 1

    if number_errors > 0:
        print(30*'*')
        print("Error with number only data")
        print(30*'*')


def read_in_csv():
    global g_allData

    with open(g_file_name, 'r') as file:
        input_data = csv.DictReader(file, delimiter = ';')
        g_allData = list(input_data)
        check_for_numbers_only()
        check_for_expected_data()

if __name__ == '__main__':
    read_in_csv()
