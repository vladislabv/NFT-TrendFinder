import logging
import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.expected_conditions import presence_of_element_located as element_located
from retry import retry

from bs4 import BeautifulSoup
import mongoengine as me


from .models import RaribleUser
from .add_extensions import SafeDict, SafeList, timing, get_picture, convert_to_int

# set logger

logging.basicConfig(
    level=logging.INFO, 
    filename='myapp.txt', 
    format='%(asctime)s %(levelname)s:%(message)s'
    )
logger = logging.getLogger(__name__)

#@dataclass
class RaribleSearchUser:
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
        self.waiter = WebDriverWait(self.driver, RaribleSearchUser.TIMEOUT_MAX)
    
    def get_url(self, url: str) -> None:
        try:
            _ = self.driver.get(url)
            logger.info(f"Requesting {url}")
        except Exception as e:
            logger.exception(e)    

    def check_exists_by_css(self, css):
        try:
            self.driver.find_element_by_css_selector(css)
        except NoSuchElementException:
            return False
        return True   

    @retry(TimeoutError, delay=2, tries=3)
    def wait_for_elements(self, type: str, elements: list[str]) -> None:
        if type == "css":
            type = By.CSS_SELECTOR
        elif type == "xpath":
            type = By.XPATH
        elif type == "class":
            type = By.CLASS_NAME
        else: 
            raise ValueError("Unknown element type!")

        for element in elements:
            locator = (type, element)
            # check if element exist
            if self.check_exists_by_css(element):
                _ = self.waiter.until( element_located(locator) )

    @timing
    @retry(exceptions=(TimeoutException), delay=2, tries=3)
    def get_page_soup(self, url: str, selectors: str, parser: str) -> str:
        #try:
        self.get_url(url)
        time.sleep(5)
        self.wait_for_elements("css", selectors)
        
        try:
            html_soup = BeautifulSoup(self.driver.page_source, parser)
            logger.info(f'Page: {url} was successfully accessed und fully loaded.')
        except Exception as e:
            html_soup = None
            logger.exception(e)
    
        return html_soup
     

    def get_user_info(self, user_ids: list[str]) -> None:
        GOT_USERS = 0
        selectors = {
            "links_css": 'div[data-marker="root/appPage/address/profile/links"] a', 
            "avatar_css": 'div[data-marker="root/appPage/address/coverAvatar/avatar"] div',
            "followers_css": 'button[data-marker="root/appPage/address/profile/followingLinks/followers"] span',
            "following_css": 'button[data-marker="root/appPage/address/profile/followingLinks/following"] span'
            }

        user_types = ['sale', 'owned', 'created']
        for type in user_types:
            selectors[f"{type}_css"] = f'button[data-marker="root/appPage/address/tabs/tab/{type}"] span'

        for id in user_ids:
            print(f'{len(user_ids)} will be found, please wait.')
            url = 'https://rarible.com/user/' + id.split(':')[-1]
            #print(url)
            # get html code from the page
            #print(selectors.values())
            soup = self.get_page_soup(
                url = url, 
                selectors = list(selectors.values()),
                parser = 'html.parser'
                )

            if soup:

                page_links = [i.get('href') for i in soup.select(selectors['links_css'])]
                page_links = page_links if len(page_links) > 0 else None
                try:
                    avatar_url = [i.find('img').get('src') for i in soup.select(selectors['avatar_css'])][0]
                except AttributeError as err:
                    print(err)
                    avatar_url = ''

                if not ( avatar_url.startswith('http') or avatar_url.startswith('https') ):
                    avatar_url = None

                owned = SafeList(
                    soup.select(selectors['owned_css'])
                    ).get(1, 0)
                sold = SafeList(
                    soup.select(selectors['sale_css'])
                    ).get(1, 0)
                created = SafeList(
                    soup.select(selectors['created_css'])
                    ).get(1, 0)

                if owned:
                    owned = convert_to_int(owned.text) if owned else owned
                if sold:
                    sold = convert_to_int(sold.text) if sold else sold
                if created:
                    created = convert_to_int(created.text) if created else created

                output = RaribleUser(
                    _id = id,
                    url = url,
                    avatar_url = avatar_url,
                    followers = convert_to_int(
                        soup.select(selectors['followers_css'])[0]
                            .text
                        ),
                    following = convert_to_int(
                        soup.select(selectors['following_css'])[0]
                            .text
                        ),
                    page_links = page_links,
                    owned = owned,
                    sold = sold,
                    created = created
                )

                try:
                    output.save()
                    GOT_USERS += 1

                    if avatar_url:
                        avatar_img = get_picture(self.avatar_url)
                        output.put(avatar_img)
                        
                except me.ValidationError as err:
                    print(err)
                    pass

                #avatar_img = get_picture(avatar_url)
                #output.avatar.put(avatar_img)

                logger.info('Going to the next user...')
        logger.info(f'{GOT_USERS} users were retrieved from the total number of {len(user_ids)}.')

#seller_ids = ["0x2d0f8e2d52c7c365e0e64d97fada66288dccb253"]

#options = Options()
#options.add_argument('--headless')
# start_date = date(2022, 3, 17)
# fetch user infos
#RaribleSearchUser(
#    "https://api.rarible.org", 
#    "C:\\Users\\vladi\\PyCourse\\NFT-Finder\\geckodriver.exe", 
#    options = options
#).get_user_info(user_ids=seller_ids)