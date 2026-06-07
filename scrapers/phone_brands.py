from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import re
import time

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")

driver = webdriver.Chrome(options=options)

url = "https://www.gsmarena.com/makers.php3"
driver.get(url)

time.sleep(3)

html = driver.page_source
driver.quit()

soup = BeautifulSoup(html, "html.parser")

brands = []
device_counts = []
links = []

for td in soup.select("td"):
    a = td.find("a")

    if not a:
        continue

    text = a.get_text(strip=True)
    match = re.match(r"(.+?)(\d+)\s+devices?", text)

    if match:
        brand = match.group(1).strip()
        device_count = int(match.group(2))

        brands.append(brand)
        device_counts.append(device_count)
        links.append("https://www.gsmarena.com/" + a["href"])

df = pd.DataFrame({
    "Brand": brands,
    "Device Count": device_counts,
    "Link": links
})

df.to_excel("phone_brands.xlsx", index=False)

print(f"Saved {len(df)} brands to phone_brands.xlsx")
print(df.head())
