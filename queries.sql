use db;

select * from db.Transaction_fact tf ;
select sum(price), tf.month , tf.year  from db.Transaction_fact tf group by tf.month, tf.year with rollup;

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
        product_category,
        city_category,
        SUM(price * quantity) AS purchase_amount
    FROM db.Transaction_fact
    GROUP BY product_category, city_category
) t1
WHERE (
    SELECT COUNT(*)
    FROM (
        SELECT 
            product_category,
            city_category,
            SUM(price * quantity) AS purchase_amount
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
-- don't wanna use a window function

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

-- Q12. Trend Analysis of Store Revenue Growth Rate Quarterly for 2017
-- Calculate the revenue growth rate for each store on a quarterly basis for 2017.

-- Q13. Detailed Supplier Sales Contribution by Store and Product Name
-- For each store, show the total sales contribution of each supplier broken down by product
-- name. The output should group results by store, then supplier, and then product name under
-- each supplier.

-- Q14. Seasonal Analysis of Product Sales Using Dynamic Drill-Down
-- Present total sales for each product, drilled down by seasonal periods (Spring, Summer, Fall,
-- Winter). This can help understand product performance across seasonal periods.

-- Q15. Store-Wise and Supplier-Wise Monthly Revenue Volatility
-- Calculate the month-to-month revenue volatility for each store and supplier pair. Volatility can be
-- defined as the percentage change in revenue from one month to the next, helping identify stores
-- or suppliers with highly fluctuating sales.

-- Q16. Top 5 Products Purchased Together Across Multiple Orders (Product Affinity
-- Analysis)
-- Identify the top 5 products frequently bought together within a set of orders (i.e., multiple
-- products purchased in the same transaction). This product affinity analysis could inform
-- potential
-- product bundling strategies.



-- Q17. Yearly Revenue Trends by Store, Supplier, and Product with ROLLUP
-- Use the ROLLUP operation to aggregate yearly revenue data by store, supplier, and product,
-- enabling a comprehensive overview from individual product-level details up to total revenue per
-- store. This query should provide an overview of cumulative and hierarchical sales figures.

-- Q18. Revenue and Volume-Based Sales Analysis for Each Product for H1 and H2
-- For each product, calculate the total revenue and quantity sold in the first and second halves of
-- the year, along with yearly totals. This split-by-time-period analysis can reveal changes in
-- product
-- popularity or demand over the year.

-- Q19. Identify High Revenue Spikes in Product Sales and Highlight Outliers
-- Calculate daily average sales for each product and flag days where the sales exceed twice the
-- daily
-- average by product as potential outliers or spikes. Explain any identified anomalies in the report,
-- as these may indicate unusual demand events.

-- Q20. Create a View STORE_QUARTERLY_SALES for Optimized Sales Analysis
-- Create a view named STORE_QUAsweRTERLY_SALES that aggregates total quarterly sales
-- by store,
-- ordered by store name. This view allows quick retrieval of store-specific trends across quarters,
-- significantly improving query performance for regular sales analysis.