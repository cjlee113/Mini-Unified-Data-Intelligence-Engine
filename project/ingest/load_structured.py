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
db_path = os.path.join(project_root, 'data/enterprise.db')
conn = duckdb.connect(db_path)

# Drop old tables if they exist
conn.execute("DROP TABLE IF EXISTS customers")
conn.execute("DROP TABLE IF EXISTS orders")
conn.execute("DROP TABLE IF EXISTS staging_customers")
conn.execute("DROP TABLE IF EXISTS staging_orders")

# Load new data
customers = pd.read_csv(os.path.join(project_root, 'data/test_data/day1_structured/input/customers.csv'))
orders = pd.read_csv(os.path.join(project_root, 'data/test_data/day1_structured/input/orders.csv'))

# Create tables
conn.execute("CREATE TABLE customers AS SELECT * FROM customers")
conn.execute("CREATE TABLE orders AS SELECT * FROM orders")
conn.execute("CREATE TABLE staging_customers AS SELECT * FROM customers")
conn.execute("CREATE TABLE staging_orders AS SELECT * FROM orders")

# Test query to verify data
result = conn.execute("""
    SELECT 
        c.name,
        c.email,
        COUNT(o.order_id) as order_count,
        SUM(o.amount) as total_spent
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.name, c.email
    ORDER BY total_spent DESC
""").df()

print("\nCustomer Orders Summary:")
print(result)

# Close the connection
conn.close()
