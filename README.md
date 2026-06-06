# 📱 Smartphone Market Research — Cross-Platform Price & Satisfaction Analysis
Cross-platform smartphone market research analyzing 1,300+ listings across Amazon, Best Buy, and Tokopedia. Investigating the relationship between price, ratings, and customer satisfaction using Excel, Python, SQL, and pandas.

> **Does paying more for a smartphone actually make you happier?** This project investigates pricing, ratings, and customer satisfaction across Amazon, Best Buy, and Tokopedia using web scraping, SQL, and Python.

---

## 🧭 Problem Statement

Consumers and brands alike assume that price is a signal of quality, that premium phones deliver premium satisfaction. This project challenges that assumption by analyzing 1,000+ smartphone listings across three major e-commerce platforms from western region concentration to southeast-asian-focused market to answer five business questions about pricing, ratings, and customer behavior.

---

## 🗂️ Dataset

| Platform | Region | Listings (Clean) |
|---|---|---|
| Amazon | US | 132 |
| Best Buy | US | 123 |
| Tokopedia | Indonesia | 1026 |
| **Total** | | 1281 |

- **Brands covered:** Samsung, Apple, Google, Motorola, Xiaomi, Oppo, Realme, vivo, Infinix, and 20+ others
- **Fields:** name, brand, price (IDR), rating, review count, platform, price tier

---

## ❓ Business Questions & Key Findings

### Does price affect customer satisfaction?
> *"Do more expensive smartphones get rated higher?"*

**Finding: No. R² = 0.0008, price explains less than 0.1% of rating variance.**

A $1,000 iPhone and a $150 budget phone are equally likely to receive the same rating. Customer satisfaction is driven by expectation vs. reality, not absolute price.

---

### Which price tier delivers the best value?

| Tier | Price Range (IDR) | Avg Rating | 5-Star Rate |
|---|---|---|---|
| Budget | < 4,500,000 | 4.74 | 54.92% |
| **Mid** | **4,500,000 – 9,000,000** | **4.82 ✅** | **47.22%** |
| Premium | 9,000,000 – 15,000,000 | 4.64 ❌ | 45.83% |
| Ultra | > 15,000,000 | 4.78 | 45.71% |

**Finding: Mid-range is the sweet spot.** Highest avg rating (4.82) at a moderate price. Premium phones are the worst performers, high price raises expectations for luxury buyers that brands fail to meet.

---

### Does more competition lower ratings?

**Finding: Hypothesis rejected.** Budget has 661 listings but doesn't have the lowest rating, Premium does (4.64) with only 72 listings. Market crowding doesn't predict satisfaction, expectation mismatch does.

---

### Do products with more reviews rate better or worse?

**Finding: Neither. R² = 0.0023, review counts[tokopedia_scrape.py](https://github.com/user-attachments/files/28659427/tokopedia_scrape.py)
[phone_brands.py](https://github.com/user-attachments/files/28659426/phone_brands.py)
[bestbuy_scrape.py](https://github.com/user-attachments/files/28659425/bestbuy_scrape.py)
 weakly affected rating, meaning more reviews doesn't mean more customers satisfaction.**

However, products with very few reviews show extreme rating variance (2.0 to 5.0), while high-review products stabilize around 3.5–5.0. Products that survive long enough to accumulate reviews tend to be good ones.

---

### Does the platform affect the price you pay?

**Finding: Yes, but due to model availability, not price gouging.**

- Tokopedia serves every segment: Rp 189,000 (Samsung entry) to Rp 1,060,000,000 (Vertu luxury)
- Best Buy skews premium: Samsung up to Rp 35.9M, Google up to Rp 29.3M
- Amazon sits in between
- Asian brands (Xiaomi, Oppo, Realme, vivo, Infinix) exist exclusively on Tokopedia

> *"Tokopedia serves everyone; Best Buy serves premium buyers, Amazon sits in between, platform choice reflects the income profile of each market."*

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python | Scraping & visualization |
| pandas | Data transformation |
| seaborn / matplotlib | Charts |
| scikit-learn | Linear regression & R² |
| Microsoft SQL Server | Data cleaning, aggregation, and business queries |
| Excel | Intermediate data storage and initial cleaning |

---

## 🚀 How to Run

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/smartphone-market-research
cd smartphone-market-research

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run web scraper & analysis
python bestbuy_scrape.py
python tokopedia_scrape.py
python phone_brands.py
python 0_price_rating_corr.py
python 0_1_review_count_rating_corr.py
```

> Update the file paths in each script to point to your local Excel output directory.

---

## 📁 Project Structure

```
smartphone-market-research/
│
├── scrapers/
│   ├── ultimate web scraper (chrome extension for Amazon web scraping)
│   ├── bestbuy_scraper.py
│   ├── tokopedia_scraper.py
|   └── phone_brands.py (scraping listings of phone brands from gsmarena)
│
├── analysis/
│   ├── 0_price_rating_corr.py
│   └── 0_1_review_count_rating_corr.py
│
├── sql/
│   └── smartphone_market.sql
│
├── Excel Output/
|   ├── amazon_research.xlsx
│   ├── bestbuy_research.xlsx
│   ├── tokopedia_research.xlsx
|   ├── phone_brands.xlsx
|   ├── amazon_bestbuy_tokopedia.xlsx
│   └── merged_class.xlsx
|
└── README.md
```

---

## 💡 Key Takeaway

> **Price is not a proxy for satisfaction.** Across 1,200+ listings on three platforms, R² = 0.0008 between price and rating. Mid-range phones deliver the highest customer satisfaction, Premium phones the lowest. Brands competing in the Rp 9M–15M range face the hardest challenge: customers arrive with high expectations and leave disappointed more often than any other tier.
