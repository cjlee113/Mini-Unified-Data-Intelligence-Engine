"""
Schema definitions for structured data tables.
"""

CUSTOMER_SCHEMA = {
    "customer_id": "INTEGER",
    "name": "VARCHAR",
    "email": "VARCHAR",
    "country": "VARCHAR"
}

ORDER_SCHEMA = {
    "order_id": "INTEGER",
    "customer_id": "INTEGER",
    "amount": "DECIMAL(10,2)",
    "order_date": "DATE"
}

# Schema validation queries
VALIDATE_CUSTOMER_EMAIL = """
SELECT customer_id, email 
FROM customers 
WHERE email NOT LIKE '%@%.%'
"""

VALIDATE_ORDER_AMOUNT = """
SELECT order_id, amount 
FROM orders 
WHERE amount <= 0
"""

# Example analytics queries
TOP_CUSTOMERS_QUERY = """
SELECT 
    c.customer_id,
    c.name,
    COUNT(o.order_id) as total_orders,
    SUM(o.amount) as total_spent
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_spent DESC
LIMIT 5
"""

COUNTRY_SALES_QUERY = """
SELECT 
    c.country,
    COUNT(DISTINCT c.customer_id) as num_customers,
    COUNT(o.order_id) as total_orders,
    SUM(o.amount) as total_revenue
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.country
ORDER BY total_revenue DESC
"""
