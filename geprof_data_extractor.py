import io
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage

import re

g_article_list = []

data_types = [
    'Artikel-Nummer',
    'Artikel-Bezeichnung',
    'Zusatz-Bezeichnung 1',
    'Kurzbezeichnung',
    'Matchcode II',
    'Warengruppe',
    'Leitartikel',
    'Größe',
    'Inhalt',
    'Gewicht',
    'Mengeneinheit',
    'Produzent',
    'Artikel-Nr Produzent',
    'Hauptlieferant',
    'Artikel-Nr Hauptlieferant',
    'Leergut-Nummer',
    'Pfand',
    'Artikelart',
    'Rückvergütung',
    'MwSt-Satz',
    'Rabattartikel',
    'Preisliste',
    'Preislisten-Nummer',
    'Aktiv',
    'Lagerort',
    'Meldebestand',
    'Höchstbestand',
    'GTIN Flasche',
    'GTIN Kiste ss Faß',
    'GTIN Palette',
    'Bemerkung',
    'ListenpreisssGrundpreis',
    'Einkaufspreis 1',
    'Einkaufspreis 2',
    'Einkaufspreis 3',
    'Kalkulation',
    'Preis 1',
    'Preis 2',
    'Preis 3',
    'Preis 4',
    'Preis 5',
    'Preis 6',
    'Preis 7',
    'Preis 8',
    'Preis 9',
    'Abholvergütung'
]

class CArticle:
    def __init__(self, first_page, second_page):
        self.first_page = first_page
        self.second_page = second_page
        self.data_dict = {
            'Artikel-Nummer': '',
            'Artikel-Bezeichnung': '',
            'Zusatz-Bezeichnung 1': '',
            'Kurzbezeichnung': '',
            'Matchcode II': '',
            'Warengruppe': '',
            'Leitartikel': '',
            'Größe': '',
            'Inhalt': '',
            'Gewicht': '',
            'Mengeneinheit': '',
            'Produzent': '',
            'Artikel-Nr Produzent': '',
            'Hauptlieferant': '',
            'Artikel-Nr Hauptlieferant': '',
            'Leergut-Nummer': '',
            'Pfand': '',
            'Artikelart': '',
            'Rückvergütung': '',
            'MwSt-Satz': '',
            'Rabattartikel': '',
            'Preisliste': '',
            'Preislisten-Nummer': '',
            'Aktiv': '',
            'Lagerort': '',
            'Meldebestand': '',
            'Höchstbestand': '',
            'GTIN Flasche': '',
            'GTIN Kiste ss Faß': '',
            'GTIN Palette': '',
            'Bemerkung': '',
            'ListenpreisssGrundpreis': '',
            'Einkaufspreis 1': '',
            'Einkaufspreis 2': '',
            'Einkaufspreis 3': '',
            'Kalkulation': '',
            'Preis 1': '',
            'Preis 2': '',
            'Preis 3': '',
            'Preis 4': '',
            'Preis 5': '',
            'Preis 6': '',
            'Preis 7': '',
            'Preis 8': '',
            'Preis 9': '',
            'Abholvergütung': ''
      }

    def clear_artikel_nummer(self):
        artikel_nummer = self.data_dict.get("Artikel-Nummer")
        listNummer = re.findall(r"\d\d\d\d\d\d\d",artikel_nummer)
        self.data_dict['Artikel-Nummer'] = listNummer
    

    def extract_data_from_pages(self):
        for idx, data_type in enumerate(data_types):
            start_idx = self.first_page.find(data_type) + len(data_type)
            if data_type != 'Abholvergütung':
                end_idx = self.first_page.find(data_types[idx + 1])
                extracted_data = self.first_page[start_idx:end_idx]
            else:
                extracted_data = self.first_page[start_idx:]

            self.data_dict[data_type] = extracted_data

        self.clear_artikel_nummer()




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

def extract_text(pdf_path):
    article_created = False
    first_page = ""
    second_page = ""

    for page in extract_text_by_page(pdf_path):
        print(page)

        if not page.find('Lieferanten-Konditionen') >= 0:

            # article without second page, create and add article
            if not article_created:
                newArticle = CArticle(first_page, "")
                newArticle.extract_data_from_pages()
                g_article_list.append(newArticle)
                article_created = True

            first_page = page
            article_created = False

        else:
            second_page = page
            newArticle = CArticle(first_page, second_page)
            newArticle.extract_data_from_pages()
            g_article_list.append(newArticle)
            article_created = True

def print_articles_list():
    for article in g_article_list:
        print(article.data_dict.get("Artikel-Nummer"))

if __name__ == '__main__':
    print(extract_text('D:\\Creativity\\Python\\geprof_data_extractor\\geprof_data.pdf'))
    print_articles_list()

