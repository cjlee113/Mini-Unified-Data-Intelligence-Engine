'''
Setup DuckDB database to customer and order data from CSV files. Run SQL queries on CSV data to 
summarize the data.
'''
import pandas as pd
import duckdb
import os

# Get project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Connect to a database
conn = duckdb.connect(os.path.join(project_root, 'data/enterprise.db'))

# Load customer data
customers = pd.read_csv(os.path.join(project_root, 'data/test_data/day1_structured/input/customers.csv'))
conn.execute("CREATE TABLE IF NOT EXISTS customers AS SELECT * FROM customers")

# Load order data
orders = pd.read_csv(os.path.join(project_root, 'data/test_data/day1_structured/input/orders.csv'))
conn.execute("CREATE TABLE IF NOT EXISTS orders AS SELECT * FROM orders")

# Save normalized tables
conn.execute("CREATE TABLE IF NOT EXISTS staging_customers AS SELECT * FROM customers")
conn.execute("CREATE TABLE IF NOT EXISTS staging_orders AS SELECT * FROM orders")

# Test query to verify data
result = conn.execute("""
    SELECT 
        c.name,
        COUNT(o.order_id) as order_count,
        SUM(o.amount) as total_spent
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.name
    ORDER BY total_spent DESC
""").df()

print("\nCustomer Orders Summary:")
print(result)

# Close the connection
conn.close()
