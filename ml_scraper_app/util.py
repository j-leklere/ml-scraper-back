import cloudscraper
from bs4 import BeautifulSoup
import math


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class Scraper:
    def __init__(self, url, results_tag, results_attr):
        self.url = url
        self.scraper = cloudscraper.create_scraper()

        print("Scrapping " + self.url)

        self.page_to_scrape = self.scraper.get(self.url)
        self.soup = BeautifulSoup(self.page_to_scrape.text, "lxml")
        num_results_h1 = self.soup.find(results_tag, results_attr, recursive=True)
        self.num_results = int(num_results_h1.text.split(" ")[0])

    def scrap_posts(self, url, posts_attr):
        self.page_to_scrape = self.scraper.get(url)
        self.soup = BeautifulSoup(self.page_to_scrape.text, "lxml")
        posts = self.soup.findAll("div", posts_attr)

        if posts:
            return posts
        else:
            print(bcolors.FAIL + "Sin resultados." + bcolors.ENDCs)
            return False

    def get_num_pages(self):
        num_pages = math.ceil(
            self.num_results / 20
        )
        print(num_pages)
        return num_pages

def output_posts_info(posts, price, address, location, expenses, all_features, link):
    print("Precio: " + price)
    if address:
        print("Dirección: " + address)
    else:
        print(bcolors.WARNING + "Dirección: Publicación sin dirección" + bcolors.ENDC)
    print("Ubicación: " + location)
    if expenses:
        print("Expensas: " + expenses)
    else:
        print(bcolors.WARNING + "Expensas: Publicación sin expensas" + bcolors.ENDC)

    if all_features:
        span_tags = all_features[0].findAll("span")
        features_str = ""
        for span in span_tags:
            features_str += span.text.strip() + " - "
        print("Otras características: " + features_str)
    else:
        print("Otras características: No disponible")

    print(link)
    print("------------------------------")