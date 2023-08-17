import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import pandas as pd



def get_article_data(link):
    r = requests.get(link, timeout=10)
    soup = BeautifulSoup(r.content, 'html.parser')
    paragraphs = soup.find_all('p')
    span = soup.find_all('span')
    article = []
    if (paragraphs is not None and len(paragraphs)) >= 2:
        for para in paragraphs:
            text = para.get_text(strip=True)
            print("paragraph", text)
            article.append(text)

    # if (span is not None and len(span)) >= 2:
    #     for s in span:
    #         text = s.get_text(strip=True)
    #         print("span", text)
    #         article.append(text)
    return article

class WebScraper:
    def __init__(self, url):
        self.url = url
        self.links = []
        self.link_data = []
        self.SPECIAL_CHAR = ["#", "sms", "tel", "mailto:"]
        
    def scrape_links(self):
        r = requests.get(self.url, timeout=50)
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
            img_element = div.find('img')
            source_element = div.find('source')
            
            if img_element or source_element:
                img_link = ""
                
                if img_element:
                    srcset_attr = img_element.get('srcset')
                    if srcset_attr:
                        img_link = srcset_attr.split()[0]
                    else:
                        img_link = img_element.get('src') or img_element.get('data-src')
                
                elif source_element:
                    srcset_attr = source_element.get('srcset')
                    if srcset_attr:
                        img_link = srcset_attr.split()[0]
                    else:
                        img_link = srcset_attr.get('src') or srcset_attr.get('data-src')
                
                paragraphs = div.find_all('p')
                heading = ""
                subheading = ""
                
                for i, para in enumerate(paragraphs):
                    text = para.text.strip()
                    if i == 0:
                        heading = text
                    elif i == 1:
                        subheading = text
                article_data = {}
                for link in div.find_all('a'):
                    href = link.get('href')
                    if href and href not in self.SPECIAL_CHAR and '/sport/' in href:
                        if not href.startswith('http'):
                            href = 'https://www.bbc.com' + '/' + href
                        if href.startswith('http'):
                            print("href:",href)
                            article_data['article_links'] = href
                            article_data['article'] = get_article_data(href)

                div_data.append({'ImageLink': img_link, 'Heading': heading, 'Subheading': subheading, 
                                 'article_links': article_data.get('article_links'), 'article':article_data.get('article')})

        return div_data


    def scrape_all_data_from_links(self):
        for link in self.links:
            r = requests.get(link, timeout=10)
            soup = BeautifulSoup(r.content, 'html.parser')
            div_data = self.scrape_divs(soup)
            self.link_data.extend(div_data)

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
scraper.save_to_excel('bbc-sport2.xlsx')
