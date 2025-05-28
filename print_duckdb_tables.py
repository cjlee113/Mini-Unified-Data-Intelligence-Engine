import duckdb

# Connect to your DuckDB database
con = duckdb.connect("project/data/enterprise.db")

# Get all table names
tables = con.execute("SHOW TABLES").fetchall()

print("Tables in DuckDB:")
for (table_name,) in tables:
    print(f"\nTable: {table_name}")
    # Print the first 5 rows from each table
    rows = con.execute(f"SELECT * FROM {table_name} LIMIT 5").fetchdf()
    print(rows)

con.close()
