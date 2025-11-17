use db;


-- Q1. Top Revenue-Generating Products on Weekdays and Weekends with Monthly Drill-Down Identifies the
-- top 5 products by revenue, split by weekdays and weekends, with monthly breakdowns for a
-- year.
(
    SELECT 
        tf.product_id, SUM(tf.price * tf.quantity) AS revenue, tf.is_weekend, tf.month, tf.year
    FROM db.Transaction_fact tf
    WHERE tf.year = 2020 AND tf.is_weekend = 0
    GROUP BY tf.product_id, tf.month, tf.year
    ORDER BY revenue DESC
    LIMIT 5
)
UNION ALL
(
    SELECT 
        tf.product_id, SUM(tf.price * tf.quantity) AS revenue, tf.is_weekend, tf.month, tf.year
    FROM db.Transaction_fact tf
    WHERE tf.year = 2020 AND tf.is_weekend = 1
    GROUP BY tf.product_id, tf.month, tf.year
    ORDER BY revenue DESC
    LIMIT 5
);
-- Q2. Customer Demographics by Purchase Amount with City Category Breakdown
-- Analyzes total purchase amounts by gender and age, detailed by city category.
SELECT 
    tf.city_category, tf.gender, tf.age, SUM(tf.price * tf.quantity) AS purchase_amount
FROM db.Transaction_fact tf
GROUP BY tf.city_category, tf.gender, tf.age WITH ROLLUP;


-- Q3. Product Category Sales by Occupation
-- Examines total sales for each product category based on customer occupation.
SELECT 
    tf.product_category, tf.occupation, SUM(tf.quantity) AS total_sales
FROM db.Transaction_fact tf
GROUP BY tf.product_category, tf.occupation WITH ROLLUP;

-- Q4. Total Purchases by Gender and Age Group with Quarterly Trend
-- Tracks purchase amounts by gender and age across quarterly periods for the current year.
SELECT 
    tf.quarter, tf.gender, tf.age, SUM(tf.price * tf.quantity) AS total_purchase
FROM db.Transaction_fact tf
GROUP BY tf.quarter, tf.gender, tf.age WITH ROLLUP;


-- Q5. Top Occupations by Product Category Sales
-- Highlights the top 5 occupations driving sales within each product category.
SELECT 
    tf.product_category, tf.occupation, SUM(tf.price * tf.quantity) AS total_sales
FROM db.Transaction_fact tf
GROUP BY tf.product_category, tf.occupation WITH ROLLUP;


-- Q6. City Category Performance by Marital Status with Monthly Breakdown
-- Assesses purchase amounts by city category and marital status over the past 6 months.
-- since tehre is no data for 2025 we will use 2020
SELECT 
    tf.year, tf.month, tf.city_category, tf.marital_status, SUM(tf.quantity * tf.price) AS purchase_amount
FROM db.Transaction_fact tf
WHERE tf.year = 2020 AND tf.month BETWEEN 5 AND 11
GROUP BY tf.year, tf.city_category, tf.marital_status, tf.month WITH ROLLUP;


-- Q7. Average Purchase Amount by Stay Duration and Gender
-- Calculates the average purchase amount based on years stayed in the city and gender.
SELECT 
    tf.stay_in_current_city_years, tf.gender, AVG(tf.price * tf.quantity) AS avg_purchase_amount
FROM db.Transaction_fact tf
GROUP BY tf.stay_in_current_city_years, tf.gender;

-- Q8. Top 5 Revenue-Generating Cities by Product Category
-- Ranks the top 5 city categories by revenue, grouped by product category.
SELECT t1.product_category, t1.city_category, t1.purchase_amount
FROM (
    SELECT 
        product_category, city_category, SUM(price * quantity) AS purchase_amount
    FROM db.Transaction_fact
    GROUP BY product_category, city_category
) t1
WHERE (
    SELECT COUNT(*)
    FROM (
        SELECT 
            product_category, city_category, SUM(price * quantity) AS purchase_amount
        FROM db.Transaction_fact
        GROUP BY product_category, city_category
    ) t2
    WHERE t2.product_category = t1.product_category
      AND t2.purchase_amount > t1.purchase_amount
) < 5
ORDER BY t1.product_category, t1.purchase_amount DESC;

-- Q9. Monthly Sales Growth by Product Category
-- Measures month-over-month sales growth percentage for each product category in the current
-- year.
SELECT 
    curr.product_category, curr.month AS current_month, curr.revenue AS current_revenue, prev.revenue AS previous_revenue,
        (curr.revenue - prev.revenue) / prev.revenue * 100 AS growth_percent
FROM (
    SELECT product_category, month, SUM(price * quantity) AS revenue
    FROM db.Transaction_fact
    WHERE year = 2020
    GROUP BY product_category, month
) curr
LEFT JOIN (
    SELECT product_category, month, SUM(price * quantity) AS revenue
    FROM db.Transaction_fact
    WHERE year = 2020
    GROUP BY product_category, month
) prev
ON curr.product_category = prev.product_category
AND curr.month = prev.month + 1
ORDER BY curr.product_category, curr.month;

-- Q10. Weekend vs. Weekday Sales by Age Group
-- Compares total sales by age group for weekends versus weekdays in the current year.
SELECT 
    tf.age, tf.is_weekend, SUM(tf.price * tf.quantity) AS total_sales
FROM db.Transaction_fact tf
WHERE tf.year = 2020
GROUP BY tf.age, tf.is_weekend
ORDER BY tf.age, tf.is_weekend;

-- Q11. Top Revenue-Generating Products on Weekdays and Weekends with Monthly Drill-
-- Down
-- Find the top 5 products that generated the highest revenue, separated by weekday and
-- weekend
-- sales, with results grouped by month for a specified year.
-- Top 5 products for weekends AND weekdays, grouped by month for a specific year (e.g., 2020)

-- Top 5 weekend products
(
    SELECT
        tf.product_id, tf.month, SUM(tf.price * tf.quantity) AS revenue, 'Weekend' AS day_type
    FROM db.Transaction_fact tf
    WHERE tf.year = 2020 AND tf.is_weekend = 1
    GROUP BY tf.product_id, tf.month
    ORDER BY revenue DESC
    LIMIT 5
)
UNION ALL
-- Top 5 weekday products
(
    SELECT
        tf.product_id, tf.month, SUM(tf.price * tf.quantity) AS revenue, 'Weekday' AS day_type
    FROM db.Transaction_fact tf
    WHERE tf.year = 2020 AND tf.is_weekend = 0
    GROUP BY tf.product_id, tf.month
    ORDER BY revenue DESC
    LIMIT 5
);

-- Q12. Trend Analysis of Store Revenue Growth Rate Quarterly for 2017
-- Calculate the revenue growth rate for each store on a quarterly basis for 2017.
-- Step 1: Get total revenue by store and quarter
SELECT 
    curr.store_id, curr.quarter AS current_quarter, curr.revenue AS current_revenue, prev.revenue AS previous_revenue, ROUND( ((curr.revenue - prev.revenue) / prev.revenue)*100, 2) AS growth_percent
FROM (
    SELECT store_id, quarter, SUM(price * quantity) AS revenue
    FROM db.Transaction_fact
    WHERE year = 2017
    GROUP BY store_id, quarter
) curr
LEFT JOIN (
    SELECT store_id, quarter, SUM(price * quantity) AS revenue
    FROM db.Transaction_fact
    WHERE year = 2017
    GROUP BY store_id, quarter
) prev ON curr.store_id = prev.store_id
AND curr.quarter = prev.quarter + 1
ORDER BY store_id, current_quarter;



-- Q13. Detailed Supplier Sales Contribution by Store and Product Name
-- For each store, show the total sales contribution of each supplier broken down by product
-- name. The output should group results by store, then supplier, and then product name under
-- each supplier.

SELECT 
    tf.store_id, tf.supplier_id, tf.product_id, SUM(tf.price * tf.quantity) AS total_sales
FROM db.Transaction_fact tf
GROUP BY tf.store_id, tf.supplier_id, tf.product_id
ORDER BY tf.store_id, tf.supplier_id, total_sales DESC;


-- Q14. Seasonal Analysis of Product Sales Using Dynamic Drill-Down
-- Present total sales for each product, drilled down by seasonal periods (Spring, Summer, Fall,
-- Winter). This can help understand product performance across seasonal periods.

SELECT 
    tf.product_id,
    CASE
        WHEN tf.month IN (3, 4, 5) THEN 'Spring'
        WHEN tf.month IN (6, 7, 8) THEN 'Summer'
        WHEN tf.month IN (9, 10, 11) THEN 'Fall'
        ELSE 'Winter'
    END AS season,
    SUM(tf.price * tf.quantity) AS total_sales
FROM db.Transaction_fact tf
WHERE year = 2020
GROUP BY tf.product_id, season with rollup
ORDER BY tf.product_id, season;


-- Q15. Store-Wise and Supplier-Wise Monthly Revenue Volatility
-- Calculate the month-to-month revenue volatility for each store and supplier pair. Volatility can be
-- defined as the percentage change in revenue from one month to the next, helping identify stores
-- or suppliers with highly fluctuating sales.

SELECT 
    curr.store_id, curr.supplier_id, curr.month AS current_month, curr.revenue AS current_revenue, prev.revenue AS previous_revenue, ROUND(((curr.revenue - prev.revenue) / prev.revenue) * 100, 2) AS volatility
FROM (
    SELECT store_id, supplier_id, month, SUM(price * quantity) AS revenue
    FROM db.Transaction_fact
    WHERE year = 2020
    GROUP BY store_id, supplier_id, month
) curr
LEFT JOIN (
    SELECT store_id, supplier_id, month, SUM(price * quantity) AS revenue
    FROM db.Transaction_fact
    WHERE year = 2020
    GROUP BY store_id, supplier_id, month
) prev
ON curr.store_id = prev.store_id
AND curr.supplier_id = prev.supplier_id
AND curr.month = prev.month + 1
ORDER BY curr.store_id, curr.supplier_id, curr.month;


-- Q16. Top 5 Products Purchased Together Across Multiple Orders (Product Affinity
-- Analysis)
-- Identify the top 5 products frequently bought together within a set of orders (i.e., multiple
-- products purchased in the same transaction). This product affinity analysis could inform
-- potential
-- product bundling strategies.

-- using a single join for pairs
-- to find, triplets, use three joins and so on
SELECT
    t1.product_id AS product_1, t2.product_id AS product_2, COUNT(*) AS times_bought_together
FROM db.Transaction_fact t1
JOIN db.Transaction_fact t2
    ON t1.id = t2.id 
GROUP BY t1.product_id, t2.product_id
ORDER BY times_bought_together DESC
LIMIT 5;


-- Q17. Yearly Revenue Trends by Store, Supplier, and Product with ROLLUP
-- Use the ROLLUP operation to aggregate yearly revenue data by store, supplier, and product,
-- enabling a comprehensive overview from individual product-level details up to total revenue per
-- store. This query should provide an overview of cumulative and hierarchical sales figures.
SELECT
    store_id, supplier_id, product_id, SUM(price * quantity) AS yearly_revenue
FROM db.Transaction_fact
WHERE year = 2020
GROUP BY store_id, supplier_id, product_id WITH ROLLUP
ORDER BY 
    store_id IS NULL, store_id,
    supplier_id IS NULL, supplier_id,
    product_id;



-- Q18. Revenue and Volume-Based Sales Analysis for Each Product for H1 and H2
-- For each product, calculate the total revenue and quantity sold in the first and second halves of
-- the year, along with yearly totals. This split-by-time-period analysis can reveal changes in
-- product
-- popularity or demand over the year.
SELECT
    product_id,
    SUM(CASE WHEN month > 0 AND month < 7 THEN price* quantity ELSE 0 END) AS revenue_h1,
    SUM (CASE WHEN month > 0 AND month < 7 THEN quantity ELSE 0 END) AS quantity_h1,
    SUM(CASE WHEN month > 6 AND month < 13 THEN quantity ELSE 0 END) AS quantity_h2,
    SUM(CASE WHEN month > 6 AND month < 13 THEN price *quantity ELSE 0 END) AS revenue_h2,
    SUM(price *quantity) AS yearly_revenue,
    SUM(quantity) AS yearly_quantity
FROM db.Transaction_fact
WHERE year = 2020
GROUP BY product_id
ORDER BY yearly_revenue DESC;



-- Q19. Identify High Revenue Spikes in Product Sales and Highlight Outliers
-- Calculate daily average sales for each product and flag days where the sales exceed twice the
-- daily
-- average by product as potential outliers or spikes. Explain any identified anomalies in the report,
-- as these may indicate unusual demand events.
WITH daily_sales AS (
    SELECT
        product_id, date, SUM(price * quantity) AS daily_revenue
    FROM db.Transaction_fact
    GROUP BY product_id, date
),
avg_sales AS (
    SELECT
        product_id,
        AVG(daily_revenue) AS avg_revenue
    FROM daily_sales
    GROUP BY product_id
)
SELECT
    d.product_id, d.date, d.daily_revenue, a.avg_revenue,
    CASE 
        WHEN d.daily_revenue > 2 * a.avg_revenue THEN 'Potential Spike'
        ELSE 'Normal'
    END AS status
FROM daily_sales d
JOIN avg_sales a ON d.product_id = a.product_id
ORDER BY product_id, date;


-- Q20. Create a View STORE_QUARTERLY_SALES for Optimized Sales Analysis
-- Create a view named STORE_QUARTERLY_SALES that aggregates total quarterly sales
-- by store,
-- ordered by store name. This view allows quick retrieval of store-specific trends across quarters,
-- significantly improving query performance for regular sales analysis.
drop view  if exists db.STORE_QUARTERLY_SALES;

CREATE VIEW db.STORE_QUARTERLY_SALES AS
SELECT
    tf.store_id,
    CONCAT('Q', CEIL(tf.month / 3)) AS q,
    SUM(tf.price * tf.quantity) AS quarterly_sales
FROM db.Transaction_fact tf
GROUP BY tf.store_id, CONCAT('Q', CEIL(tf.month / 3));

SELECT * FROM db.STORE_QUARTERLY_SALES
ORDER BY store_id, q;

