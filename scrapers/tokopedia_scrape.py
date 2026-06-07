from playwright.sync_api import sync_playwright
import pandas as pd
import json
import re

URL = "https://www.tokopedia.com/search?q=smartphone&st=product&navsource=&srp_component_id=02.01.00.00&srp_page_id=&srp_page_title=&navsource=category&sc=89"

captured = []
products = []

def deep_find_products(obj):
    found = []

    if isinstance(obj, dict):
        if "name" in obj and ("price" in obj or "url" in obj):
            found.append(obj)

        for v in obj.values():
            found.extend(deep_find_products(v))

    elif isinstance(obj, list):
        for i in obj:
            found.extend(deep_find_products(i))

    return found


# rating + sold parsers

def extract_rating_from_text(text):
    if not text:
        return None
    match = re.search(r"\b([0-5]\.\d)\b", text)
    if match:
        return match.group(1)
    return None


def extract_sold_from_text(text):
    if not text:
        return None

    match = re.search(r"(\d+\s?rb\+)", text, re.IGNORECASE)
    if match:
        return match.group(1).replace(" ", "")

    match2 = re.search(r"(\d+)\s*terjual", text, re.IGNORECASE)
    if match2:
        return match2.group(1)

    return None


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)

    context = browser.new_context(
        viewport={"width": 1366, "height": 768},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36"
    )

    page = context.new_page()

    
    # capture json
    
    def on_response(response):
        try:
            ct = response.headers.get("content-type", "")
            if "application/json" in ct:
                data = response.json()
                captured.append(data)
        except:
            pass

    page.on("response", on_response)

    print("Loading page...")
    page.goto(URL, wait_until="domcontentloaded")
    page.wait_for_timeout(10000)

    # scroll to bottom + click "Muat Lebih Banyak"
    for click_round in range(20): # exactly 20 times
        print(f"Round {click_round + 1}/3 — scrolling to bottom...")

        # scroll to bottom
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(3000)

        # try to click the load more button
        button_found = False
        for label in ["Muat Lebih Banyak", "Load More", "Lihat Lebih Banyak"]:
            try:
                btn = page.locator(f"button:has-text('{label}')").first
                btn.wait_for(state="visible", timeout=5000)
                btn.scroll_into_view_if_needed()
                page.wait_for_timeout(1000)
                btn.click()
                print(f"  ✔ Clicked '{label}' (round {click_round + 1})")
                page.wait_for_timeout(5000)
                button_found = True
                break
            except:
                continue

        if not button_found:
            print(f"  ✗ Button not found in round {click_round + 1} — trying JS click...")
            try:
                page.evaluate("""
                    const buttons = [...document.querySelectorAll('button')];
                    const btn = buttons.find(b => b.innerText.includes('Muat') || b.innerText.includes('Load More'));
                    if (btn) btn.click();
                """)
                print(f"  ✔ JS click attempted")
                page.wait_for_timeout(5000)
            except:
                print(f"  ✗ JS click also failed — skipping round")

    # final scroll to capture everything loaded
    print("Final scroll to capture all loaded products...")
    for step in range(1, 10):
        page.evaluate(f"window.scrollTo(0, {step * 800})")
        page.wait_for_timeout(500)
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(5000)

    browser.close()
    print("Browser closed.")


# analyze data

print("Captured responses:", len(captured))

for blob in captured:
    items = deep_find_products(blob)

    for p in items:
        try:
            price = p.get("price", {})

            raw_text = str(p)

            products.append({
                "Name": p.get("name"),
                "Price": price.get("text") if isinstance(price, dict) else None,
                "Original Price": price.get("original") if isinstance(price, dict) else None,
                "Rating": extract_rating_from_text(raw_text),
                "Units Sold": extract_sold_from_text(raw_text),
                "Link": p.get("url")
            })

        except:
            pass


# export

df = pd.DataFrame(products).drop_duplicates()

cleaned = []
i = 0
while i < len(df):
    product_row = df.iloc[i].to_dict()

    if i + 1 < len(df):
        next_row = df.iloc[i + 1]
        is_brand_row = (
            pd.isna(next_row["Price"]) and
            pd.isna(next_row["Rating"]) and
            pd.isna(next_row["Units Sold"])
        )
        if is_brand_row:
            product_row["Brand"] = next_row["Name"]
            i += 2
        else:
            product_row["Brand"] = None
            i += 1
    else:
        product_row["Brand"] = None
        i += 1

    cleaned.append(product_row)

df_clean = pd.DataFrame(cleaned)

cols = ["Name", "Brand", "Price", "Original Price", "Rating", "Units Sold", "Link"]
df_clean = df_clean[[c for c in cols if c in df_clean.columns]]

df_clean.to_excel("tokopedia_research.xlsx", index=False)

print("DONE ✔")
print("Products:", len(df_clean))
