from cgitb import reset
import logging
from functools import wraps
import time
from datetime import datetime, date

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.expected_conditions import presence_of_element_located as element_located
from retry import retry

from bs4 import BeautifulSoup
import scrapy
from scrapy.loader import ItemLoader
from items import RaribleNftItem, RaribleUser

from dotenv import load_dotenv
from pathlib import Path
import os

# set logger

logging.basicConfig(
    level=logging.INFO, 
    filename='myapp.txt', 
    format='%(asctime)s %(levelname)s:%(message)s'
    )
logger = logging.getLogger(__name__)


def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        print('func:%r args:[%r, %r] took: %2.4f sec' % \
          (f.__name__, args, kw, te-ts)
        )
        return result
    return wrap

#@dataclass
class RaribleSearch(scrapy.Spider):
    #path_driver: str = None
    #options: 'Selenium.WebDriver.Options' = None
    TIMEOUT_MAX = 10
    MAX_RETRIES = 3
    DELAY_IN_RETRIES = 2

    def __init__(self, base_url: str, path_driver: str = None, options = None):
        self.base_url = base_url
        self.driver = webdriver.Firefox(executable_path = path_driver, options = options)
        #self.driver.set_page_load_timeout = self.TIMEOUT_MAX
        logger.info('The webdriver is open.')
        self.waiter = WebDriverWait(self.driver, 5)
    
    def get_url(self, url: str) -> None:
        try:
            _ = self.driver.get(url)
            logger.info(f"Requesting {url}")
        except Exception as e:
            logger.exception(e)       

    #@timing
    def wait_for_element(self, type: str, element: str) -> None:
        if type == "css":
            type = By.CSS_SELECTOR
        elif type == "xpath":
            type = By.XPATH
        elif type == "class":
            type = By.CLASS_NAME
        else: 
            raise ValueError("Unknown element type!")
        
        locator = (type, element)

        _ = self.waiter.until( element_located(locator) )

    @timing
    @retry(TimeoutException, delay=DELAY_IN_RETRIES, tries=MAX_RETRIES)
    def get_page_soup(self, url: str, css_selector: str, parser: str) -> str:
        try:
            self.get_url(url)
            self.wait_for_element("css", css_selector)
            logger.info(f'Page: {url} was successfully accessed und fully loaded.')
        except (TimeoutException, Exception) as e:
            logger.exception(e)
        
        try:
            html_soup = BeautifulSoup(self.driver.page_source, parser)
        except Exception as e:
            html_soup = None
            logger.exception(e)

        return html_soup

    def top_sellers(self) -> list[str]:

        selector_sellers = 'div[data-marker = "root/appPage/marketplace"] > div > div > div:nth-child(4) > div:nth-child(2) a'

        soup = self.get_page_soup(
            url = "https://rarible.com", 
            css_selector = selector_sellers,
            parser = 'html.parser'
            )

        links = []

        for item in soup.select(selector_sellers):
            url = self.base_url + item.get('href')
            if "/collection/" not in url and url not in links:
                links.append(url)
                logger.info(f'{url} was added to the Top Sellers List.')
        
        logger.info(f'{len(links)} URLs were fetched.')

        return links

    def activity_items(self, top_urls: list[str], start_date: datetime.date) -> None:
        
        selector_items = 'div[role="rowgroup"].ReactVirtualized__Grid__innerScrollContainer > div'

        SCROLL_PAUSE_TIME = 0.5

        for url in top_urls:
            act_url = url + '/activity'
            count_items = 0
            while True:
                # Get scroll height
                last_height = self.driver.execute_script("return document.body.scrollHeight")

                # get html code from the page
                soup = self.get_page_soup(
                    url = act_url, 
                    css_selector = selector_items,
                    parser = 'html.parser'
                    )
                if soup:
                    logger.info(f'Fetching data from {act_url}')
                    for row in soup.select(selector_items):
                        a_tags = row.find_all('a')
                        span_tags = row.find_all('span')
                        add_info = [i.get('title') for i in span_tags if i.get('title') is not None]
                        fetched_urls = set(filter(lambda x: 'token' in x, [i.get('href') for i in a_tags]))
                        img_links = [item.get('src') for sublist in [i.findAll('img') for i in a_tags] for item in sublist]
                        # define variables because they are variative
                        sold_date = None
                        sold_price = None
                        picture_usr = None
                        picture_item = None
                        used_currency = None

                        for i in add_info:
                            try:
                                sold_date = datetime.strptime(i, "%d.%m.%Y, %H:%M:%S")
                            except ValueError as e:
                                try:
                                    sold_price_list = i.split(' ')
                                    sold_price = float(sold_price_list[0])
                                    used_currency = sold_price_list[-1]
                                except ValueError as e:
                                    pass

                        if any(s for s in img_links if 'avatar' in s):
                            picture_usr = [s for s in img_links if 'avatar' in s][0]
                        if any(s for s in img_links if 'itemImages' in s):
                            picture_item = [s for s in img_links if 'itemImages' in s][0]
                            
                        # filter out activies have nothing to do with sell
                        if sold_price and sold_date.date() >= start_date:
                            if not count_items:
                                logger.info('Following data were fetched')
                            count_items += 1
                            item_url = self.base_url + list(fetched_urls)[0]
                            il = RaribleNftItem(
                                id = item_url.split('/')[-1],
                                url = item_url,
                                picture = picture_item,
                                date = sold_date,
                                price = sold_price,
                                currency = used_currency
                            )
                            logger.info(f'Item {count_items}:\n')
                            logger.info(il.__dict__)

                            i2 = RaribleUser(
                                id = url.split('/')[-1],
                                picture = picture_usr,
                                url = url
                            )

                            logger.info(f'User {count_items}:\n')
                            logger.info(i2.__dict__)

                # Scroll down to bottom
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                # Wait to load page
                time.sleep(SCROLL_PAUSE_TIME)
                # Calculate new scroll height and compare with last scroll height
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                # stop looping if height has not changed, i.e. the end of the page is reached
                if last_height == new_height:
                    break
                else:
                    last_height = new_height
            if count_items:
                logger.info(f'For page {act_url} {count_items} after {start_date} are extracted.')
            else:
                logger.warning(f'For page {act_url} no items could be extracted.')

            logger.info('Going to the next page...')


if __name__ == '__main__':
    # all variables from .env will be loaded into environment
    load_dotenv(Path('./.env'))

    options = Options()
    options.add_argument('--headless')
    _path = os.getenv('DRIVER_PATH')
    _base_url = os.getenv('BASE_URL')

    start_date = date(2022, 3, 17)

    sellers = RaribleSearch(_base_url, _path, options)

    top_urls = sellers.top_sellers()

    sold_items = sellers.activity_items(top_urls, start_date)

    #self.driver.quit()
    #logger.info('The webdriver is closed.')

    print(top_urls)
