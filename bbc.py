import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import pandas as pd

class WebScraper:
    def __init__(self, url):
        self.url = url
        self.links = []
        self.link_data = []
        self.SPECIAL_CHAR = ["#", "sms", "tel", "mailto:"]
        
    def scrape_links(self):
        r = requests.get(self.url, timeout=30)
        soup = BeautifulSoup(r.content, 'html.parser')
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and href not in self.SPECIAL_CHAR:
                if not href.startswith('http'):
                    href = self.url + '/' + href
                if href.startswith('http'):
                    self.links.append(href)

    def scrape_divs(self, soup):
        div_data = []
        for div in soup.find_all('div'):
            source_element = div.find('source')
            img_element = div.find('img')
            paragraphs = div.find_all('p')
            if (img_element and len(paragraphs) >= 2) : 
                img_link = ""
                srcset_attr = img_element.get('srcset')
                if srcset_attr:
                    img_link = srcset_attr.split()[0]
                    
                heading = paragraphs[0].text.strip()
                subheading = ' '
                for sub in paragraphs[1:]:
                    subheading += sub.text.strip()
                div_data.append({'ImageLink': img_link, 'Heading': heading, 'Subheading': subheading})
            if (source_element and len(paragraphs) >= 2) : 
                img_link = ""
                srcset_attr = source_element.get('srcset')
                if srcset_attr:
                    img_link = srcset_attr.split()[0]
                heading = paragraphs[0].text.strip()
                subheading = ' '
                for sub in paragraphs[1:]:
                    subheading += sub.text.strip()
                div_data.append({'ImageLink': img_link, 'Heading': heading, 'Subheading': subheading})

        return div_data

    def scrape_all_data_from_links(self):
        for link in self.links:
            r = requests.get(link)
            soup = BeautifulSoup(r.content, 'html.parser')
            div_data = self.scrape_divs(soup)
            self.link_data.extend(div_data)
        unique_data = [dict(t) for t in {tuple(d.items()) for d in self.link_data}]
        self.link_data = unique_data

    def save_to_excel(self, file_name):
        self.scrape_links()
        self.scrape_all_data_from_links()

        try:
            existing_df = pd.read_excel(file_name)
            combined_df = pd.concat([existing_df, pd.DataFrame(self.link_data)], ignore_index=True)
            combined_df.to_excel(file_name, index=False)
            print(f"Data appended to {file_name} file.")
        except FileNotFoundError:
            df = pd.DataFrame(self.link_data)
            df.to_excel(file_name, index=False)
            print(f"File {file_name} does not exist. Created a new file with the scraped data.")


scraper = WebScraper('https://www.bbc.com/sport')
scraper.save_to_excel('bbc-sport.xlsx')
