import duckdb

class SQLRetriever:
    def __init__(self, duckdb_path):
        self.conn = duckdb.connect(duckdb_path)

    def search(self, query, top_k=3):
        # Simple SQL search for customer names containing the query string
        result = self.conn.execute(
            f"""
            SELECT * FROM customers
            WHERE name ILIKE '%{query}%'
            LIMIT {top_k}
            """
        ).fetchdf().to_dict('records')
        return result 