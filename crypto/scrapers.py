from decimal import Decimal
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

def bitcoin_fee():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    with webdriver.Chrome(options=options) as driver:
        driver.get("https://mempool.space/")
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "green-color")))
        html_content = driver.page_source
    
    soup = BeautifulSoup(html_content, "html.parser")
    fees = soup.find_all("span", class_="green-color ng-star-inserted")
    
    results = {
        "low": Decimal(fees[1].text.replace("$", "")),
        "medium": Decimal(fees[2].text.replace("$", "")),
        "high": Decimal(fees[3].text.replace("$", ""))
    }
    
    return results


