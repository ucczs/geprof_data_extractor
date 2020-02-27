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
data_types = [
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
    'Mengeneinheit:',
    'Produzent:',
    'Artikel-Nr Produzent',
    'Hauptlieferant:',
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
    'Einkaufspreis 1:',
    'Einkaufspreis 2:',
    'Einkaufspreis 3:',
    'Kalkulation:',
    'Preis 1:',
    'Preis 2:',
    'Preis 3:',
    'Preis 4:',
    'Preis 5:',
    'Preis 6:',
    'Preis 7:',
    'Preis 8:',
    'Preis 9:',
    'Abholvergütung:'
]


# class for articles
class CArticle:
    def __init__(self, first_page, second_page):
        # raw extracted text info from pdf
        self.first_page = first_page
        self.second_page = second_page

        # dictionary to file with data found in the pdf
        self.lieferaten_konditionen = []

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
            'Produzent:': '',
            'Artikel-Nr Produzent': '',
            'Hauptlieferant:': '',
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
            'ListenpreisssGrundpreis:': '',
            'Einkaufspreis 1:': '',
            'Einkaufspreis 2:': '',
            'Einkaufspreis 3:': '',
            'Kalkulation:': '',
            'Preis 1:': '',
            'Preis 2:': '',
            'Preis 3:': '',
            'Preis 4:': '',
            'Preis 5:': '',
            'Preis 6:': '',
            'Preis 7:': '',
            'Preis 8:': '',
            'Preis 9:': '',
            'Abholvergütung:': ''
      }
  

    # extract data from first page
    def extract_data_from_first_page(self):
        for idx, data_type in enumerate(data_types):
            start_idx = self.first_page.find(data_type) + len(data_type)
            if data_type != 'Abholvergütung:':
                end_idx = self.first_page.find(data_types[idx + 1])
                
                # only extract article number, no date
                if data_type == 'Artikel-Nummer:':
                    extracted_data = self.first_page[start_idx:end_idx].replace("    ", " ").replace("   ", " ").replace("  ", " ")[:9]
                else:
                    extracted_data = self.first_page[start_idx:end_idx]
            else:
                extracted_data = self.first_page[start_idx:].replace(":", "")

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
                # print(self.data_dict["Artikel-Bezeichnung:"])
                # print(begin_idx)
                if cnt < len(list_of_lieferanten_konditionen_idx) - 1:
                    self.lieferaten_konditionen.append(self.second_page[begin_idx:list_of_lieferanten_konditionen_idx[cnt + 1]])
                else:
                    self.lieferaten_konditionen.append(self.second_page[begin_idx:])


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
            newArticle.first_page = ""
            newArticle.second_page = ""

            g_article_list.append(newArticle)
            article_created = True


def generate_output_file():
    global g_output_string

    for data_type in data_types:
        g_output_string += (data_type + ";")

    for i in range(1,51):
        g_output_string += (str(i) + ". Lieferanten-Konditionen;")

    g_output_string += "\n"
    output_file_cnt = 0

    for article in g_article_list:
        
        # debug output to see some progress
        output_file_cnt += 1
        if output_file_cnt % 50 == 0:
            print("Article " + str(output_file_cnt) + " of " + str(len(g_article_list)) + " written to output string.")

        # list, append and join is used for speed up (concatenation is very slow)
        data_types_list = []
        for data_type in data_types:
            data_types_list.append(article.data_dict.get(data_type))
        g_output_string += (';'.join(data_types_list) + ";")
        
        # list, append and join is used for speed up (concatenation is very slow)
        lieferaten_kondition_list = []
        for lieferaten_kondition in article.lieferaten_konditionen:
            lieferaten_kondition_list.append(lieferaten_kondition)
        g_output_string += (';'.join(lieferaten_kondition_list) + ";")

        g_output_string += "\n"

    g_output_string = g_output_string.replace("; ", ";").replace("\n ", "\n").replace("\"", "").replace(" ;", ";")
    output_file = open("output.csv","w+")
    output_file.write(g_output_string)
    output_file.close()


if __name__ == '__main__':
    # print(extract_text('.\\geprof_data.pdf'))
    print(extract_text('.\\all_articles.pdf'))
    # print_articles_list()
    generate_output_file()