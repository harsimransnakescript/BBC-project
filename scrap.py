import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pandas as pd

class WebScraper:
    def __init__(self, url):
        self.url = url
        self.links = []
        self.link_text_dict = {}
        self.link_image_dict = {}
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

    def scrape_images_from_url(self, url):
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        img_urls = [img['src'] for img in soup.find_all('img', src=True)]
        return img_urls
    
    def scrape_all_images_from_links(self):
        for link in self.links:
            img_urls = self.scrape_images_from_url(link)
            if not img_urls: 
                img_urls = ['']
            parsed_url = urlparse(link)
            key_name = parsed_url.path
            self.link_image_dict[key_name] = img_urls

    def scrape_div_content(self, soup):
        div_texts = []
        for div in soup.find_all('div'):
            div_text = div.get_text().replace('\n', '').replace('\t', '').replace('\r', '').strip()
            if div_text:
                div_text = div_text.encode('ascii', 'ignore').decode()
                div_texts.append(div_text)
        return div_texts
    
    def scrape_all_text_from_links(self):
        for link in self.links:
            r = requests.get(link)
            soup = BeautifulSoup(r.content, 'html.parser')

            div_texts = self.scrape_div_content(soup)

            parsed_url = urlparse(link)
            key_name = parsed_url.path
            self.link_text_dict[key_name] = {'text': div_texts}

    def scrape_text_from_url(self, url):
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        all_text = soup.get_text().replace('\n', '').replace('\t', '').replace('\r','').strip()
        all_text = all_text.encode('ascii', 'ignore').decode()
        return all_text

    def scrape_all_text_from_links(self):
        self.main_url_text = self.scrape_text_from_url(self.url)
        self.link_text_dict['main_url'] = {'text': self.main_url_text}
        for link in self.links:
            r = requests.get(link)
            soup = BeautifulSoup(r.content, 'html.parser')
            paragraphs = soup.find_all('p')  # Extract paragraphs from the page
            
            all_paragraphs = []
            for paragraph in paragraphs:
                paragraph_text = paragraph.get_text().replace('\n', '').replace('\t', '').replace('\r', '').strip()
                if paragraph_text:  # Skip empty paragraphs
                    paragraph_text = paragraph_text.encode('ascii', 'ignore').decode()
                    all_paragraphs.append(paragraph_text)
            
            parsed_url = urlparse(link)
            key_name = parsed_url.path
            self.link_text_dict[key_name] = {'text': all_paragraphs}


    def save_to_excel(self, file_name):
        self.scrape_links()
        self.scrape_all_text_from_links()
        self.scrape_all_images_from_links()

        new_data = []
        for link_name in self.link_text_dict:
            text = self.link_text_dict[link_name]['text']
            image_urls = ', '.join(self.link_image_dict.get(link_name, []))
            new_data.append({'Link Name': link_name, 'Text': text, 'ImageURL': image_urls})

        try:
            existing_df = pd.read_excel(file_name)
            combined_df = pd.concat([existing_df, pd.DataFrame(new_data)], ignore_index=True)
            combined_df.to_excel(file_name, index=False)
            print(f"Data appended to {file_name} file.")
        except FileNotFoundError:
            df = pd.DataFrame(new_data)
            df.to_excel(file_name, index=False)
            print(f"File {file_name} does not exist. Created a new file with the scraped data.")

urls = ['https://www.bbc.com/', 'https://www.bbc.com/sport', 'https://www.bbc.com/reel']

excel_file_name = 'bbc-scrap-data.xlsx'
try:
    existing_df = pd.read_excel(excel_file_name)
except FileNotFoundError:
    existing_df = pd.DataFrame(columns=['Link Name', 'Text', 'ImageURL'])
    
for url in urls:
    scraper = WebScraper(url)
    scraper.save_to_excel(excel_file_name)
