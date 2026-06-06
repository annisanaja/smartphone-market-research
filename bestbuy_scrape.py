from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

option = webdriver.ChromeOptions()
option.add_argument("--window-size=1300,800")
option.add_argument("--disable-blink-features=AutomationControlled")
option.add_experimental_option("excludeSwitches", ["enable-automation"])
option.add_experimental_option("useAutomationExtension", False)
option.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=option)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

base_url = "https://www.bestbuy.com"
bestbuy_link = "https://www.bestbuy.com/site/unlocked-mobile-phones/all-unlocked-cell-phones/pcmcat311200050005.c?id=pcmcat311200050005"
driver.set_window_size(1300, 800)
driver.get(bestbuy_link)

list_name = []
list_price = []
list_link = []
list_reviewcount = []
list_rating = []

def scrape_current_page():
    # scroll slowly to load all products
    for i in range(1, 20):
        driver.execute_script(f"window.scrollTo(0, {500 * i})")
        time.sleep(2)
    time.sleep(2)

    content = driver.page_source
    data = BeautifulSoup(content, 'html.parser')

    seen_names = set()  # track duplicates per page

    for area in data.find_all('div', class_="sku-block-content"):
        name_tag = area.find('h3', attrs={"class": lambda c: c and "product-title" in c})
        if not name_tag:
            continue

        name = name_tag.get_text(strip=True)
        if not name or name in seen_names:  # skip empty or duplicate
            continue
        seen_names.add(name)

        price_tag = area.find('span', class_="font-sans text-default text-style-body-md-400 sr-only")
        price = price_tag.get_text() if price_tag else None

        link_tag = area.find('a', class_="product-list-item-link")
        link = link_tag['href'] if link_tag else None

        reviewcount_tag = area.find('span', class_="c-reviews order-2")
        reviewcount = reviewcount_tag.get_text() if reviewcount_tag else None

        rating = area.find('p', class_="visually-hidden")
        if rating != None:
            rating = rating.get_text()

        list_name.append(name)
        list_price.append(price)
        list_link.append(link)
        list_reviewcount.append(reviewcount)
        list_rating.append(rating)
        print(f"Added: {name}")

    print(f"Total so far: {len(list_name)}")

# scrape per page
print("Scraping page 1...")
for page in range(1, 43):
    print(f"Scraping page {page}...")
    url = f"https://www.bestbuy.com/site/unlocked-mobile-phones/all-unlocked-cell-phones/pcmcat311200050005.c?id=pcmcat311200050005&cp={page}"
    driver.get(url)
    time.sleep(4)
    scrape_current_page()

driver.quit()

df = pd.DataFrame({
    'Name': list_name,
    'Price': list_price,
    'Link': list_link,
    'Review_Count': list_reviewcount,
    'Rating': list_rating
})

print(f"Total items scraped: {len(df)}")

with pd.ExcelWriter('bestbuy_research.xlsx') as writer:
    df.to_excel(writer, sheet_name='Sheet1', index=False)

print("Saved to bestbuy_research.xlsx")