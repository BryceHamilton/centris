from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


driver = webdriver.Chrome('./chromedriver')

def fetch_with_selenium():
    
    driver.get("https://centris.ca/en/triplexes~for-sale~montreal-island")

    parse_with_soup(driver.page_source)

    next_button = driver.find_element(By.CLASS_NAME, "next")
    next_button.click()

    prop = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "thumbnailItem")))

    # parse_with_soup(driver.page_source)

    


def parse_with_soup(text):
    # headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 12_4_0; en-US; Valve Steam Tenfoot/1658440720; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}
    # r = requests.get("https://centris.ca/en/triplexes~for-sale~montreal-island", headers=headers)

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
        ratio = rev / price
        results.append((ratio, price, f"https://www.centris.ca{link}"))

    results.sort(key=lambda x : -x[0])
    for r in results:
        print(r)


fetch_with_selenium()