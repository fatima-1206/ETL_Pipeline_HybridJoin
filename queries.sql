use db;

select * from db.Transaction_fact tf ;
select sum(price), tf.`month` , tf.`year`  from db.Transaction_fact tf group by tf.month, tf.year with rollup;

-- Q1. Top Revenue-Generating Products on Weekdays and Weekends with Monthly Drill-Down Identifies the
-- top 5 products by revenue, split by weekdays and weekends, with monthly breakdowns for a
-- year.
(select tf.product_id, sum(tf.price*tf.quantity) as revenue, tf.is_weekend , tf.month, tf.year  
from db.Transaction_fact tf 
group by tf.product_id, tf.is_weekend , tf.`month`, tf.year with rollup
having tf.year = 2020 and tf.is_weekend =0
order by revenue desc
limit 5)
union all
(select tf.product_id, sum(tf.price*tf.quantity) as revenue, tf.is_weekend , tf.month, tf.year  
from db.Transaction_fact tf 
group by tf.product_id, tf.is_weekend , tf.`month`, tf.year with rollup
having tf.year = 2020 and tf.is_weekend =1
order by revenue desc
limit 5);
-- Q2. Customer Demographics by Purchase Amount with City Category Breakdown
-- Analyzes total purchase amounts by gender and age, detailed by city category.

select sum(tf.price*tf.quantity) as purchase_ammount, tf.age, tf.gender,  tf.city_category
from db.Transaction_fact tf 
group by city_category , gender, age with rollup;

-- Q3. Product Category Sales by Occupation
-- Examines total sales for each product category based on customer occupation.
select sum(tf.quantity) as total_sales, tf.product_category, tf.occupation 
from db.Transaction_fact tf 
group by tf.occupation , tf.product_category with rollup;
-- Q4. Total Purchases by Gender and Age Group with Quarterly Trend
-- Tracks purchase amounts by gender and age across quarterly periods for the current year.
select sum(tf.price*tf.quantity) as purchase_ammount, tf.age, tf.gender, tf.quarter
from db.Transaction_fact tf 
group by tf.quarter , tf.gender, tf.age with rollup;
-- Q5. Top Occupations by Product Category Sales
-- Highlights the top 5 occupations driving sales within each product category.
select sum(tf.quantity*tf.price) as total_sales, tf.product_category, tf.occupation 
from db.Transaction_fact tf 
group by tf.occupation , tf.product_category with rollup;



-- Q6. City Category Performance by Marital Status with Monthly Breakdown
-- Assesses purchase amounts by city category and marital status over the past 6 months.
-- since tehre is no data for 2025 we will use 2020
select sum(tf.quantity*tf.price) as purchase_ammounts, tf.`month`, tf.marital_status, tf.`year` 
from db.Transaction_fact tf 
group by tf.year, tf.marital_status , tf.`month` with rollup
having tf.year = 2020 and tf.`month` BETWEEN 5 AND 11;

-- Q7. Average Purchase Amount by Stay Duration and Gender
-- Calculates the average purchase amount based on years stayed in the city and gender.
select avg(tf.price*tf.quantity) as avg_purchase_ammount, tf.stay_in_current_city_years, tf.gender
from db.Transaction_fact tf
group by tf.gender,tf.stay_in_current_city_years ;

-- Q8. Top 5 Revenue-Generating Cities by Product Category
-- Ranks the top 5 city categories by revenue, grouped by product category.

-- Q9. Monthly Sales Growth by Product Category
-- Measures month-over-month sales growth percentage for each product category in the current
-- year.

-- Q10. Weekend vs. Weekday Sales by Age Group
-- Compares total sales by age group for weekends versus weekdays in the current year.

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