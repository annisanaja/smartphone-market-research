SELECT *
FROM MarketResearch..phone_brands phone_brands

SELECT *
FROM MarketResearch..tokopedia_cleaned tokopedia

SELECT *
FROM phone_brands
WHERE Brand = 'HP'

DELETE FROM phone_brands
WHERE Brand = 'HP'

-- check Brand from tokopedia scraped data
WITH tokopedia AS (
	SELECT t.*, p.Brand
    FROM tokopedia_cleaned t
    OUTER APPLY (
        SELECT TOP 1 p.Brand
        FROM phone_brands p
        WHERE t.Name LIKE '%' + p.Brand + '%'
        ORDER BY LEN(p.Brand) DESC
    ) p
)

SELECT *
INTO tokopedia_data
FROM tokopedia

-- view tokopedia_data after brand looked up
SELECT *
FROM tokopedia_data
ORDER BY Name

-- 17 Brand is NULL
SELECT *
FROM tokopedia_data
WHERE Brand is NULL
ORDER BY Name

-- 344 isn't looked up properly due to mispelling
SELECT *
FROM tokopedia_data
WHERE Brand = 'O'
ORDER BY Name

-- delete mispelled and null Brand data from tokopedia_data
DELETE FROM tokopedia_data
WHERE Brand IS NULL

DELETE FROM tokopedia_data
WHERE Brand = 'O'

-- tokopedia_data after being cleaned
SELECT *
FROM tokopedia_data
-- 1066 data left
-- issue is that BLU brand is returned from "Bluetooth" = invalid data

-- check BLU Brand from tokopedia_data
SELECT *
FROM tokopedia_data
WHERE Brand = 'BLU'
-- 34 data contain mischecked Bluetooth to be identified as BLU Brand

-- delete data containing BLU Brand
DELETE FROM tokopedia_data
WHERE Brand = 'BLU'

-- 1032 data after fully cleansed
select *
from tokopedia_data

-- do the same for brands from Amazon
WITH amazon AS (
	SELECT a.*, p.Brand AS brand_name
    FROM MarketResearch..amazon_cleaned a
    OUTER APPLY (
        SELECT TOP 1 p.Brand
        FROM phone_brands p
        WHERE a.product_desc LIKE '%' + p.Brand + '%'
        ORDER BY LEN(p.Brand) DESC
    ) p
)

INSERT INTO amazon_data
SELECT *
FROM amazon

-- view amazon_data
SELECT *
FROM amazon_data
ORDER BY brand_name

-- 146 data is not null, 96 is null
SELECT *
FROM amazon_data
WHERE product_desc is NOT null

DELETE FROM amazon_data
WHERE product_desc IS NULL

-- 14 data of none smartphone items is parsed from the previous web scraping process
-- delete those data
SELECT *
FROM amazon_data
WHERE brand_name = 'O'

DELETE FROM amazon_data
WHERE brand_name = 'O'

-- 132 data remaining from Amazon source
SELECT *
FROM amazon_data
ORDER BY brand_name

-- delete the initially parsed Brand data from Amazon sourced dataset
ALTER TABLE amazon_data
DROP COLUMN Brand

-- view bestbuy data
SELECT *
FROM bestbuy_cleaned
ORDER BY Brand

DELETE FROM bestbuy_cleaned
WHERE Name IS NULL
-- 44 out of 167 data removed (blank datas), 123 data remaining from BestBuy source
-- No issues from Brand data collected over BestBuy

-- view all data from 3 sources: tokopedia, bestbuy, amazon
SELECT *
FROM amazon_data
WHERE RATING <= 5
ORDER BY brand_name

SELECT *
FROM bestbuy_cleaned
WHERE RATING <= 5
ORDER BY Brand

SELECT *
FROM tokopedia_data
WHERE RATING <= 5
ORDER BY Brand

-- merge 3 tables
WITH merged AS (
    SELECT 
        product_desc as name,
        brand_name as brand,
        rating,
        review_count,
        price_idr,
        source
    FROM amazon_data
    UNION ALL
    SELECT
        Name as name,
        Brand as brand,
        Rating as rating,
        Review_Count as review_count,
        Price_IDR as price_idr,
        Source as source
    FROM bestbuy_cleaned
    UNION ALL
    SELECT
        Name as name,
        Brand as brand,
        Rating as rating,
        [Units Sold] as review_count,
        Price as price_idr,
        Source as source
    FROM tokopedia_data
)

SELECT *
INTO merged_data
FROM merged
-- 1287 data merged

-- price tier vs avg rating
SELECT *
FROM merged_data

WITH class_v_rating AS (
    SELECT *,
        CASE
            WHEN price_idr <= 4500000 THEN 'Budget'
            WHEN price_idr > 4500000 AND price_idr <= 9000000 THEN 'Mid'
            WHEN price_idr > 9000000 AND price_idr <= 15000000 THEN 'Premium'
            ELSE 'Ultra'
        END AS class
    FROM merged_data
    WHERE rating <= 5
),
stats AS (
    SELECT
        class,
        COUNT(*) AS total_records,
        AVG(rating) AS avg_rating,
        MIN(rating) AS min_rating,
        MAX(rating) AS max_rating
    FROM class_v_rating
    GROUP BY class
),
counts AS (
    SELECT
        c.class,
        SUM(CASE WHEN c.rating = s.min_rating THEN 1 ELSE 0 END) AS count_min,
        SUM(CASE WHEN c.rating = s.max_rating THEN 1 ELSE 0 END) AS count_max
    FROM class_v_rating c
    JOIN stats s ON c.class = s.class
    GROUP BY c.class
)

SELECT
    s.class,
    s.total_records,
    ROUND(s.avg_rating, 2) AS avg_rating,
    s.min_rating,
    s.max_rating,
    CONCAT(ROUND(CAST(100.0 * c.count_min AS FLOAT) / s.total_records, 2), '%') AS pct_min_rating,
    CONCAT(ROUND(CAST(100.0 * c.count_max AS FLOAT) / s.total_records, 2), '%') AS pct_max_rating
FROM stats s
JOIN counts c ON s.class = c.class
ORDER BY s.class

-- Mid wins. Highest avg rating (4.82) at moderate price: best value tier.
-- Premium disappoints. Lowest avg rating (4.64) despite high price: expectations exceed reality.
-- Paying more ≠ more satisfied. Ultra (4.78) beats Premium despite costing more, Budget (4.74) nearly matches it at a fraction of the price.
-- 5-star rates drop as price rises —> 41.87% -> 38.99% -> 31.13%: harder to impress expensive buyers.

WITH class_v_rating AS (
    SELECT *,
        CASE
            WHEN price_idr <= 4500000 THEN 'Budget'
            WHEN price_idr > 4500000 AND price_idr <= 9000000 THEN 'Mid'
            WHEN price_idr > 9000000 AND price_idr <= 15000000 THEN 'Premium'
            ELSE 'Ultra'
        END AS class
    FROM merged_data
    WHERE rating <= 5
)

SELECT
    class,
    AVG(rating) AS avg_rating,
    AVG(review_count) AS avg_review_count,
    ROUND(
        (AVG(CAST(rating AS FLOAT) * review_count) - AVG(CAST(rating AS FLOAT)) * AVG(review_count)) /
        (STDEV(CAST(rating AS FLOAT)) * STDEV(review_count))
    , 4) AS correlation
FROM class_v_rating
GROUP BY class
ORDER BY class

-- do different platforms provide different price ranges?
WITH class_v_rating AS (
    SELECT *,
        CASE
            WHEN price_idr <= 4500000 THEN 'Budget'
            WHEN price_idr > 4500000 AND price_idr <= 9000000 THEN 'Mid'
            WHEN price_idr > 9000000 AND price_idr <= 15000000 THEN 'Premium'
            ELSE 'Ultra'
        END AS class
    FROM merged_data
    WHERE rating <= 5
)

SELECT
    brand,
    CONCAT(
        FORMAT(MIN(CASE WHEN source = 'Amazon' THEN CAST(price_idr AS FLOAT) END), 'N0'),
        ' - ',
        FORMAT(MAX(CASE WHEN source = 'Amazon' THEN CAST(price_idr AS FLOAT) END), 'N0')
    ) AS amazon_price_range,

    CONCAT(
        FORMAT(MIN(CASE WHEN source = 'BestBuy' THEN CAST(price_idr AS FLOAT) END), 'N0'),
        ' - ',
        FORMAT(MAX(CASE WHEN source = 'BestBuy' THEN CAST(price_idr AS FLOAT) END), 'N0')
    ) AS bestbuy_price_range,

    CONCAT(
        FORMAT(MIN(CASE WHEN source = 'Tokopedia' THEN CAST(price_idr AS FLOAT) END), 'N0'),
        ' - ',
        FORMAT(MAX(CASE WHEN source = 'Tokopedia' THEN CAST(price_idr AS FLOAT) END), 'N0')
    ) AS tokopedia_price_range

FROM class_v_rating
GROUP BY brand
ORDER BY brand

-- Tokopedia serves everyone
-- Best Buy serves premium buyers 
-- Amazon sits in between
-- Platform choice reflects the income profile of each market

