from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException


driver = webdriver.Chrome('./chromedriver')

PRICE_MAX_OFFSET = 80
APPR_RATE = 0.03


def set_price():
    driver.find_element(By.ID, "SalePrice-button").click()
    sleep(1) 
    slider = driver.find_element(By.CLASS_NAME, "max-slider-handle")
    ActionChains(driver).drag_and_drop_by_offset(slider, -PRICE_MAX_OFFSET, 0).perform()
    sleep(1) 
    driver.find_element(By.CLASS_NAME, "btn-search").click()

def setup():
    driver.get("https://centris.ca/en/triplexes~for-sale~montreal-island")
    set_price()
    

def navigate_next():
    
    sleep(1)
    next_button = driver.find_element(By.CLASS_NAME, "next")
    next_button.click()

    loaded = False
    while not loaded:
        loaded = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "thumbnailItem")))

    

def is_next():
    next_button = driver.find_element(By.CLASS_NAME, "next")
    classes = next_button.get_attribute("class").split()
    return "inactive" not in classes


def fetch_properties():
    properties = []

    next_properties = parse_properties(driver.page_source)
    properties += next_properties

    while is_next():
        next_properties = parse_properties(driver.page_source)
        properties += next_properties
        navigate_next()
        sleep(0.1)

    properties.sort(key=lambda x : x.total_ratio)
    return properties


class Listing(object):
    def __init__(self, price, rev, link):
        self.price = price
        self.rev = rev
        self.ratio = rev / price
        self.monthly = rev / 12
        self.appr = price * APPR_RATE / 12
        self.total_monthly = self.monthly + self.appr
        self.total_ratio = self.total_monthly * 12 / self.price
        self.link = link
    def __repr__(self):
        return f"""
        Total Ratio: {self.total_ratio}
        Rent Ratio: {self.ratio}
        Price: ${self.price}
        Rent Monthly: ${self.monthly}
        Apprec.: ${self.appr}
        Link: {self.link}


        """

def parse_properties(text):
    
    soup = BeautifulSoup(text, features="html.parser")

    properties = soup.find_all("div", {"class": "thumbnailItem"})

    results = []
    for property in properties:
        link = property.find("a", {"class": "a-more-detail"})["href"]
        address_span = property.find_all("span")[3]
        # neighbourhood = address_span.find_all("div")[2]
        rev = int(property.find_all("span")[4].text.split("Pot. Gross Rev.: $")[1].replace(",", ""))
        price_section = property.find("div", {"class": "price"})
        price = int(price_section.find("span").text.replace("$", "").replace(",", ""))
        link = f"https://www.centris.ca{link}"
        listing = Listing(price, rev, link)
        results.append(listing)

    return results


def print_results(results):
    for result in results:
        print(result)


def main():
    setup()
    sleep(1)
    results = fetch_properties()
    print_results(results)
    driver.quit()

main()