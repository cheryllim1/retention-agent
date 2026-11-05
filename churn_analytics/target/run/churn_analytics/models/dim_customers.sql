
  
  create view "analytics"."main"."dim_customers__dbt_tmp" as (
    WITH customer_orders AS (
    SELECT
        "User_ID" AS customer_id,
        MAX(CAST("Purchase_Date" AS DATE)) AS last_purchase_date,
        COUNT(*) AS total_orders,
        SUM(CAST("Final_Price(Rs.)" AS DOUBLE)) AS total_spend,
        AVG(CAST("Discount (%)" AS DOUBLE)) AS avg_discount_used
    FROM raw_orders
    WHERE "User_ID" IS NOT NULL
    GROUP BY "User_ID"
)

SELECT
    customer_id,
    total_orders,
    ROUND(total_spend, 2) AS total_spend,
    ROUND(avg_discount_used, 2) AS avg_discount_used,
    last_purchase_date,
    DATEDIFF('day', last_purchase_date, (SELECT MAX(CAST("Purchase_Date" AS DATE)) FROM raw_orders)) AS days_since_last_order,
    CASE 
        WHEN DATEDIFF('day', last_purchase_date, (SELECT MAX(CAST("Purchase_Date" AS DATE)) FROM raw_orders)) > 180 THEN 'High Churn Risk'
        WHEN DATEDIFF('day', last_purchase_date, (SELECT MAX(CAST("Purchase_Date" AS DATE)) FROM raw_orders)) BETWEEN 90 AND 180 THEN 'Medium Churn Risk'
        ELSE 'Active'
    END AS churn_risk_status
FROM customer_orders
  );
