import duckdb

# Connect to (or create) a local DuckDB database file
con = duckdb.connect('analytics.duckdb')

# Load the CSV file into a DuckDB table
con.execute("""
    CREATE OR REPLACE TABLE raw_orders AS 
    SELECT * FROM read_csv_auto('ecommerce_dataset_updated.csv')
""")

print("Dataset successfully ingested into DuckDB!")

# Quick check to see the first 5 rows and column names
preview = con.execute("SELECT * FROM raw_orders LIMIT 5").df()
print("\n--- Data Preview ---")
print(preview)