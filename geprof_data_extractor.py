import io
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage

import re

# list of all articles (type CArticle)
g_article_list = []

# collect all infos in this global string
g_output_string = ''

# list of data types in the pdf
g_data_types = [
    'Artikel-Nummer:',
    'Artikel-Bezeichnung:',
    'Zusatz-Bezeichnung 1:',
    'Kurzbezeichnung:',
    'Matchcode II:',
    'Warengruppe:',
    'Leitartikel:',
    'Größe:',
    'Inhalt:',
    'Gewicht:',
    'input_only_Mengeneinheit:',                # input only, no output
    'output_only_Mengeneinheit Nr:',            # output only, no read in from pdf
    'output_only_Mengeneinheit Ki:',            # output only, no read in from pdf
    'output_only_Mengeneinheit Fl:',            # output only, no read in from pdf
    'output_only_Mengeneinheit Pal:',           # output only, no read in from pdf
    'output_only_Mengeneinheit Lage:',          # output only, no read in from pdf
    'output_only_Mengeneinheit Bezeichnung:',   # output only, no read in from pdf
    'input_only_Produzent:',                    # input only, no output
    'output_only_Produzent-Nr:',                # output only, no read in from pdf
    'output_only_Produzent-Name:',              # output only, no read in from pdf
    'Artikel-Nr Produzent',
    'input_only_Hauptlieferant:',               # input only, no output
    'output_only_Hauptlieferant-Nr:',           # output only, no read in from pdf
    'output_only_Hauptlieferant-Name:',         # output only, no read in from pdf
    'Artikel-Nr Hauptlieferant:',
    'Leergut-Nummer:',
    'Pfand:',
    'Artikelart',
    'Rückvergütung:',
    'MwSt-Satz:',
    'Rabattartikel:',
    'Preisliste:',
    'Preislisten-Nummer:',
    'Aktiv:',
    'Lagerort:',
    'Meldebestand:',
    'Höchstbestand:',
    'GTIN Flasche:',
    'GTIN Kiste / Faß:',
    'GTIN Palette:',
    'Bemerkung:',
    'Listenpreis/Grundpreis:',
    'output_only_Listenpreis/Grundpreis Fl:',
    'output_only_Listenpreis/Grundpreis Kommentar:',
    'Einkaufspreis 1:',
    'output_only_Einkaufspreis 1 Fl:',
    'Einkaufspreis 2:',
    'output_only_Einkaufspreis 2 Fl:',
    'Einkaufspreis 3:',
    'output_only_Einkaufspreis 3 Fl:',
    'input_only_Kalkulation:',
    'Preis 1:',
    'output_only_Preis 1 Fl:',
    'Preis 2:',
    'output_only_Preis 2 Fl:',
    'Preis 3:',
    'output_only_Preis 3 Fl:',
    'Preis 4:',
    'output_only_Preis 4 Fl:',
    'Preis 5:',
    'output_only_Preis 5 Fl:',
    'Preis 6:',
    'output_only_Preis 6 Fl:',
    'Preis 7:',
    'output_only_Preis 7 Fl:',
    'Preis 8:',
    'output_only_Preis 8 Fl:',
    'Preis 9:',
    'output_only_Preis 9 Fl:',
    'Abholvergütung:'
]

# define substrings which should be removed from a specific data type
g_remove_dict = {
    'Größe:': 'Stück',
    'Inhalt:': 'Liter',
    'Gewicht:': 'Kilogramm',
    'Meldebestand:': 'Einheiten',
    'Höchstbestand:': 'Einheiten',
    'Pfand:': 'EUR'
}


# class for lieferanten-konditionen
class CLieferanten_kondi:
    def __init__(self, raw_text):
        self.raw_text = raw_text
        self.data_dict_lieferanten_kondi = {
            'Lieferanten-Konditionen Kondi-Gültigkeit': '',
            'Lieferanten-Konditionen Kondi': '',
            'Lieferanten-Konditionen Auf-/Abschlag': '',
            'Lieferanten-Konditionen Wert': '',
            'Lieferanten-Konditionen Einheit': '',
            'Lieferanten-Konditionen Geltungsbereich': '',
            'Lieferanten-Konditionen Bezeichnung': ''
        }


# class for articles
class CArticle:
    def __init__(self, first_page, second_page):
        # raw extracted text info from pdf
        self.first_page = first_page
        self.second_page = second_page

        # dictionary to file with data found in the pdf
        self.lieferanten_konditionen_raw = []
        self.lieferanten_konditionen_split_up = []

        self.data_dict = {
            'Artikel-Nummer:': '',
            'Artikel-Bezeichnung:': '',
            'Zusatz-Bezeichnung 1:': '',
            'Kurzbezeichnung:': '',
            'Matchcode II:': '',
            'Warengruppe:': '',
            'Leitartikel:': '',
            'Größe:': '',
            'Inhalt:': '',
            'Gewicht:': '',
            'Mengeneinheit:': '',
            'Mengeneinheit Nr:': '',            # data extracted from "Mengeneinheit"
            'Mengeneinheit Ki:': '',            # data extracted from "Mengeneinheit"
            'Mengeneinheit Fl:': '',            # data extracted from "Mengeneinheit"
            'Mengeneinheit Pal:': '',           # data extracted from "Mengeneinheit"
            'Mengeneinheit Lage:': '',          # data extracted from "Mengeneinheit"
            'Mengeneinheit Bezeichnung:': '',   # data extracted from "Mengeneinheit"
            'Produzent:': '',
            'Produzent-Nr:': '',                # data extracted from "Produzent"
            'Produzent-Name:': '',              # data extracted from "Produzent"
            'Artikel-Nr Produzent': '',
            'Hauptlieferant:': '',
            'Hauptlieferant-Nr:': '',           # data extracted from "Hauptlieferant"
            'Hauptlieferant-Name:': '',         # data extracted from "Hauptlieferant"
            'Artikel-Nr Hauptlieferant:': '',
            'Leergut-Nummer:': '',
            'Pfand:': '',
            'Artikelart': '',
            'Rückvergütung:': '',
            'MwSt-Satz:': '',
            'Rabattartikel:': '',
            'Preisliste:': '',
            'Preislisten-Nummer:': '',
            'Aktiv:': '',
            'Lagerort:': '',
            'Meldebestand:': '',
            'Höchstbestand:': '',
            'GTIN Flasche:': '',
            'GTIN Kiste / Faß:': '',
            'GTIN Palette:': '',
            'Bemerkung:': '',
            'Listenpreis/Grundpreis:': '',
            'Listenpreis/Grundpreis Fl:': '',
            'Listenpreis/Grundpreis Kommentar:': '',
            'Einkaufspreis 1:': '',
            'Einkaufspreis 1 Fl:': '',
            'Einkaufspreis 2:': '',
            'Einkaufspreis 2 Fl:': '',
            'Einkaufspreis 3:': '',
            'Einkaufspreis 3 Fl:': '',
            'Kalkulation:': '',
            'Preis 1:': '',
            'Preis 1 Fl:': '',
            'Preis 2:': '',
            'Preis 2 Fl:': '',
            'Preis 3:': '',
            'Preis 3 Fl:': '',
            'Preis 4:': '',
            'Preis 4 Fl:': '',
            'Preis 5:': '',
            'Preis 5 Fl:': '',
            'Preis 6:': '',
            'Preis 6 Fl:': '',
            'Preis 7:': '',
            'Preis 7 Fl:': '',
            'Preis 8:': '',
            'Preis 8 Fl:': '',
            'Preis 9:': '',
            'Preis 9 Fl:': '',
            'Abholvergütung:': ''
      }


    # extract data from first page
    def extract_data_from_first_page(self):
        for idx, data_type in enumerate(g_data_types):
            
            # skip data types which are marked as output_only_
            if data_type.find("output_only_") >= 0:
                continue

            # remove prefix for input_only flag
            data_type = data_type.replace("input_only_", "")

            start_idx = self.first_page.find(data_type) + len(data_type)
            if data_type != 'Abholvergütung:':
                next_valid_input_type = 1

                while(g_data_types[idx + next_valid_input_type].find("output_only_") >= 0):
                    next_valid_input_type += 1

                end_idx = self.first_page.find(g_data_types[idx + next_valid_input_type].replace("input_only_", ""))
                
                # only extract article number, no date
                if data_type == 'Artikel-Nummer:':
                    extracted_data = self.first_page[start_idx:end_idx].replace("    ", " ").replace("   ", " ").replace("  ", " ")[:9]
                else:
                    extracted_data = self.first_page[start_idx:end_idx]
            else:
                extracted_data = self.first_page[start_idx:].replace(":", "")

            # remove substrings which are always present in the data_type (e.g. EUR, Liter...)
            for remove_from_data_type in g_remove_dict.keys():
                if data_type.find(remove_from_data_type) >= 0:
                    extracted_data = extracted_data.replace(g_remove_dict[remove_from_data_type], "")

            # clear MwSt-Satz data
            if data_type.find("MwSt-Satz:") >= 0:
                if extracted_data.find("19.00") >= 0:
                    extracted_data = "19"
                elif extracted_data.find("7.00") >= 0:
                    extracted_data = "7"
                elif extracted_data.find("0.00") >= 0:
                    extracted_data = "0"

            extracted_data = extracted_data.replace("    ", " ").replace("   ", " ").replace("  ", " ").replace("  ", " ").replace(":", "")
            self.data_dict[data_type] = extracted_data


    # extract data from second page
    # search for <number> ". Ja" or <number> ". Nein"
    def extract_data_from_second_page(self):
        list_of_lieferanten_konditionen_idx = []
        if self.second_page != "":
            idx = 0
            for i in range(1,51):
                if i < 10:
                    number_template_1 = " " + str(i) + ". Ja"
                    number_template_2 = " " + str(i) + ". Nein"
                else:
                    number_template_1 = str(i) + ". Ja"
                    number_template_2 = str(i) + ". Nein"
                  
                idx_1 = self.second_page.find(number_template_1, idx + 1)
                idx_2 = self.second_page.find(number_template_2, idx + 1)
                if idx_1 < 0 and idx_2 >= 0:
                    idx = idx_2
                elif idx_2 < 0 and idx_1 >= 0:
                    idx = idx_1
                else:
                    idx = min(idx_1, idx_2)

                if idx >= 0:
                    list_of_lieferanten_konditionen_idx.append(idx)

            for cnt, begin_idx in enumerate(list_of_lieferanten_konditionen_idx):
                if cnt < len(list_of_lieferanten_konditionen_idx) - 1:
                    self.lieferanten_konditionen_raw.append(self.second_page[begin_idx:list_of_lieferanten_konditionen_idx[cnt + 1]])
                else:
                    self.lieferanten_konditionen_raw.append(self.second_page[begin_idx:])

            self.split_up_lieferanten_kondi()


    def split_up_lieferanten_kondi(self):
        for lieferanten_kondition in self.lieferanten_konditionen_raw:
            lieferanten_kondition.replace("   ", " ").replace("  ", " ")
            newLieferantenKondi = CLieferanten_kondi(lieferanten_kondition)

            # Lieferanten-Konditionen Kondi-Gültigkeit
            kondi_string_before = ""
            if lieferanten_kondition.find(". Ja") >= 0:
                newLieferantenKondi.data_dict_lieferanten_kondi['Lieferanten-Konditionen Kondi-Gültigkeit'] = 'Ja'
                kondi_start_idx = lieferanten_kondition.find("Ja") + 2
            elif lieferanten_kondition.find(". Nein") >= 0:
                newLieferantenKondi.data_dict_lieferanten_kondi['Lieferanten-Konditionen Kondi-Gültigkeit'] = 'Nein'
                kondi_start_idx = lieferanten_kondition.find("Nein") + 4

            # Lieferanten-Konditionen Auf-/Abschlag
            if lieferanten_kondition.find("./.") >= 0:
                kondi_end_idx = lieferanten_kondition.find("./.")
                newLieferantenKondi.data_dict_lieferanten_kondi['Lieferanten-Konditionen Auf-/Abschlag'] = './.'
                wert_start_idx = lieferanten_kondition.find("./.") + 3

            elif lieferanten_kondition.find("+") >= 0:
                kondi_end_idx = lieferanten_kondition.find("+")
                newLieferantenKondi.data_dict_lieferanten_kondi['Lieferanten-Konditionen Auf-/Abschlag'] = '+'
                wert_start_idx = lieferanten_kondition.find("+") + 1

            # Lieferanten-Konditionen Kondi
            newLieferantenKondi.data_dict_lieferanten_kondi['Lieferanten-Konditionen Kondi'] = lieferanten_kondition[kondi_start_idx:kondi_end_idx].strip()

            # Lieferanten-Konditionen Einheit
            if lieferanten_kondition.find("%") >= 0:
                einheit_end_idx = lieferanten_kondition.find("%") + 1
                einheit_start_idx = lieferanten_kondition.find("%")
                newLieferantenKondi.data_dict_lieferanten_kondi['Lieferanten-Konditionen Einheit'] = "%"
            elif lieferanten_kondition.find("EUR") >= 0:
                einheit_start_idx = lieferanten_kondition.find("EUR")
                einheit_end_idx = lieferanten_kondition[lieferanten_kondition.find("EUR") + 1:].find(" ") + lieferanten_kondition.find("EUR") + 1
                einheit = lieferanten_kondition[einheit_start_idx:einheit_end_idx]
                newLieferantenKondi.data_dict_lieferanten_kondi['Lieferanten-Konditionen Einheit'] = einheit

            # Lieferanten-Konditionen Wert
            newLieferantenKondi.data_dict_lieferanten_kondi['Lieferanten-Konditionen Wert'] = lieferanten_kondition[wert_start_idx:einheit_start_idx]

            # Lieferanten-Konditionen Geltungsbereich
            geltungsbereich_string = lieferanten_kondition[einheit_end_idx:].strip()
            geltungsbereich_idx_end = geltungsbereich_string.find(" ")
            newLieferantenKondi.data_dict_lieferanten_kondi['Lieferanten-Konditionen Geltungsbereich'] = geltungsbereich_string[:geltungsbereich_idx_end].strip()

            # Lieferanten-Konditionen Bezeichnung
            newLieferantenKondi.data_dict_lieferanten_kondi['Lieferanten-Konditionen Bezeichnung'] = geltungsbereich_string[geltungsbereich_idx_end + 1:].strip()

            self.lieferanten_konditionen_split_up.append(newLieferantenKondi)


    # format of produzent and hauptlieferant:
    # 01234 Name
    # split up number and name
    def split_up_produ_hauptl(self):
        split_up_data_types = ['Produzent:', 'Hauptlieferant:']
        for split_up_data_type in split_up_data_types:
            original_data = self.data_dict[split_up_data_type].strip()
            data_type_nr = original_data[:original_data.find(" ")]
            data_type_name = original_data[original_data.find(" "):]

            self.data_dict[split_up_data_type[:-1] + '-Nr:'] = data_type_nr
            self.data_dict[split_up_data_type[:-1] + '-Name:'] = data_type_name


    def split_up_mengeneinheit(self):
        original_data = self.data_dict['Mengeneinheit:'].strip()

        self.data_dict['Mengeneinheit Nr:'] = original_data[:find_nth(original_data, " ", 1)]
        self.data_dict['Mengeneinheit Ki:'] = original_data[find_nth(original_data, " ", 1)+1:find_nth(original_data, " ", 2)]
        self.data_dict['Mengeneinheit Fl:'] = original_data[find_nth(original_data, " ", 2)+1:find_nth(original_data, " ", 3)]
        self.data_dict['Mengeneinheit Pal:'] = original_data[find_nth(original_data, " ", 3)+1:find_nth(original_data, " ", 4)]
        self.data_dict['Mengeneinheit Lage:'] = original_data[find_nth(original_data, " ", 4)+1:find_nth(original_data, " ", 5)]
        self.data_dict['Mengeneinheit Bezeichnung:'] = original_data[find_nth(original_data, " ", 5)+1:]

    
    def split_up_einkaufspreis(self):
        einkaufspreise_cnt = 3
        for i in range(1, einkaufspreise_cnt + 1):
            type_name_ek = 'Einkaufspreis ' + str(i) + ':'
            type_name_ek_fl = 'Einkaufspreis ' + str(i) + ' Fl:'

            original_data = self.data_dict[type_name_ek]
            if original_data.find("Fl") >= 0:
                self.data_dict[type_name_ek] = original_data[:original_data.find("Fl") - 1]
                self.data_dict[type_name_ek_fl] = original_data[original_data.find("Fl") + 3:]
            else:
                continue


    def split_up_preis(self):
        preise_cnt = 9
        for i in range(1, preise_cnt + 1): 
            type_name_preis = 'Preis ' + str(i) + ':'
            type_name_preis_fl = 'Preis ' + str(i) + ' Fl:'

            original_data = self.data_dict[type_name_preis]
            self.data_dict[type_name_preis] = original_data[original_data.find("Brutto") + 7:original_data.find("|")-1]
            self.data_dict[type_name_preis_fl] = original_data[original_data.find("Fl") + 2:]


    def split_up_listenpreis_grundpreis(self):
        self.data_dict['Listenpreis/Grundpreis Kommentar:'] = self.data_dict['Kalkulation:']
        
        original_data = self.data_dict['Listenpreis/Grundpreis:']

        if original_data.find("Fl") >= 0:
            self.data_dict['Listenpreis/Grundpreis:'] = original_data[:original_data.find('Fl') - 1]
            self.data_dict['Listenpreis/Grundpreis Fl:'] = original_data[original_data.find('Fl') + 3:original_data.find('=')]
        else:
            self.data_dict['Listenpreis/Grundpreis:'] = original_data[:original_data.find('=') - 1]


    def split_up_combined_infos(self):
        self.split_up_produ_hauptl()
        self.split_up_mengeneinheit()
        self.split_up_einkaufspreis()
        self.split_up_preis()
        self.split_up_listenpreis_grundpreis()


# help function to find nth occurence of substring
def find_nth(input_string, substring, n):
    start = input_string.find(substring)
    while start >= 0 and n > 1:
        start = input_string.find(substring, start+len(substring))
        n -= 1
    return start


# function for reading in pdf as text
def extract_text_by_page(pdf_path):
    with open(pdf_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh, 
                                      caching=True,
                                      check_extractable=True):
            resource_manager = PDFResourceManager()
            fake_file_handle = io.StringIO()
            converter = TextConverter(resource_manager, fake_file_handle)
            page_interpreter = PDFPageInterpreter(resource_manager, converter)
            page_interpreter.process_page(page)
            
            text = fake_file_handle.getvalue()
            yield text
    
            # close open handles
            converter.close()
            fake_file_handle.close()


# pdf to text and text processing function
def extract_text(pdf_path):
    article_created = False
    first_page = ""
    second_page = ""

    number_page = 0

    for page in extract_text_by_page(pdf_path):

        # debug output to see some progress
        number_page += 1
        if number_page % 50 == 0:
            print("Page " + str(number_page) + " extracted")
        # print(page)

        if not page.find('Lieferanten-Konditionen') >= 0:

            # article without second page, create and add article
            if not article_created:
                newArticle = CArticle(first_page, "")
                newArticle.extract_data_from_first_page()
                newArticle.split_up_combined_infos()
                newArticle.first_page = ""
                g_article_list.append(newArticle)
                article_created = True

            first_page = page
            article_created = False

        else:
            second_page = page
            newArticle = CArticle(first_page, second_page)
            newArticle.extract_data_from_first_page()
            newArticle.extract_data_from_second_page()
            newArticle.split_up_combined_infos()
            newArticle.first_page = ""
            newArticle.second_page = ""

            g_article_list.append(newArticle)
            article_created = True


def generate_output_file():
    global g_output_string

    # Abholvergütung is not necessary
    g_data_types.remove("Abholvergütung:")

    # remove data_types for input_only
    # and remove prefix "output_only_"
    remove_list = []
    for idx, data_type in enumerate(g_data_types):
        g_data_types[idx] = data_type.replace("output_only_", "")
        if data_type.find("input_only_") >= 0:
            remove_list.append(data_type)
    for remove_data in remove_list:
        g_data_types.remove(remove_data)

    # create headings for output csv
    for data_type in g_data_types:
        if data_type == "Inhalt:":
            data_type = "Inhalt (Liter):"
        if data_type == "Gewicht:":
            data_type = "Gewicht (kg):"
        if data_type == "Pfand:":
            data_type = "Pfand (€):"
        if data_type == "MwSt-Satz:":
            data_type = "MwSt-Satz (%):"
        g_output_string += (data_type + ";")

    for i in range(1,51):
        g_output_string += (str(i) + ". Lieferanten-Konditionen Kondi-Gültigkeit;")
        g_output_string += (str(i) + ". Lieferanten-Konditionen Kondi;")
        g_output_string += (str(i) + ". Lieferanten-Konditionen Auf-/Abschlag;")
        g_output_string += (str(i) + ". Lieferanten-Konditionen Wert;")
        g_output_string += (str(i) + ". Lieferanten-Konditionen Einheit;")
        g_output_string += (str(i) + ". Lieferanten-Konditionen Geltungsbereich;")
        g_output_string += (str(i) + ". Lieferanten-Konditionen Bezeichnung;")

    g_output_string += "\n"
    output_file_cnt = 0

    for article in g_article_list:
        
        # output to see some progress 
        output_file_cnt += 1
        if output_file_cnt % 50 == 0:
            print("Article " + str(output_file_cnt) + " of " + str(len(g_article_list)) + " written to output string.")

        # list, append and join is used for speed up (concatenation is very slow)
        data_types_list = []
        for data_type in g_data_types:
            data_types_list.append(article.data_dict.get(data_type))
        g_output_string += (';'.join(data_types_list) + ";")
        
        # list, append and join is used for speed up (concatenation is very slow)
        for lieferanten_kondition in article.lieferanten_konditionen_split_up:
            lieferanten_kondition_list = []
            for kondi_data in lieferanten_kondition.data_dict_lieferanten_kondi.keys():
                lieferanten_kondition_list.append(lieferanten_kondition.data_dict_lieferanten_kondi[kondi_data])
            g_output_string += (';'.join(lieferanten_kondition_list) + ";")

        g_output_string += "\n"

    g_output_string = g_output_string.replace("; ", ";").replace("\n ", "\n").replace("\"", "").replace(" ;", ";")
    output_file = open("output.csv","w+")
    output_file.write(g_output_string)
    output_file.close()


if __name__ == '__main__':
    print(extract_text('.\\geprof_data.pdf'))
    # print(extract_text('.\\all_articles.pdf'))
    generate_output_file()