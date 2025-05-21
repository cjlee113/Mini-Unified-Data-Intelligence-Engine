from neo4j import GraphDatabase
from dotenv import load_dotenv
import os
import logging
import re
import duckdb

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Load environment variables
load_dotenv()
URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")
driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

# Dummy tool classes
def SQLTool(query):
    # If the query is about 'who ordered the most in Japan', run a real SQL query
    if "ordered the most in japan" in query.lower():
        con = duckdb.connect()
        csv_path = "project/data/day1_structured/input/orders.csv"
        con.execute(f"CREATE OR REPLACE TABLE orders AS SELECT * FROM read_csv_auto('{csv_path}')")
        result = con.execute("""
            SELECT customer, SUM(amount) as total_amount
            FROM orders
            WHERE country = 'Japan'
            GROUP BY customer
            ORDER BY total_amount DESC
            LIMIT 1
        """).fetchone()
        con.close()
        if result:
            return f"Customer who ordered the most in Japan: {result[0]} (Total: {result[1]})"
        else:
            return "No orders found for Japan."
    return f"[SQLTool] Executed SQL query: {query}"

def VectorTool(query):
    return f"[VectorTool] Performed vector search for: {query}"

def GraphTool(query):
    # Improved logic: handle 'Who works at <Company>?' queries robustly
    match = re.match(r"who works at (.+)\??", query.strip(), re.IGNORECASE)
    if match:
        company = match.group(1).strip().rstrip('?')
        cypher = (
            "MATCH (p:Person)-[:WORKS_AT]->(c:Company) "
            "WHERE toLower(c.name) = toLower($company) "
            "RETURN p.name AS name"
        )
        with driver.session() as session:
            result = session.run(cypher, company=company)
            people = [record["name"] for record in result]
        return f"People who work at {company}: {', '.join(people) if people else 'None found'}"
    else:
        return f"[GraphTool] No logic for this query yet: {query}"

# Simple router agent
def route_query(query):
    if any(word in query.lower() for word in ["order", "customer", "jan"]):
        tool = SQLTool
        tool_name = "SQLTool"
    elif any(word in query.lower() for word in ["vector", "embedding", "similarity"]):
        tool = VectorTool
        tool_name = "VectorTool"
    elif any(word in query.lower() for word in ["graph", "entity", "relationship", "works at"]):
        tool = GraphTool
        tool_name = "GraphTool"
    else:
        tool = lambda q: "[Default] No suitable tool found."
        tool_name = "None"
    logging.info(f"Input: {query}")
    logging.info(f"Tool used: {tool_name}")
    output = tool(query)
    logging.info(f"Output: {output}\n")
    return output

if __name__ == "__main__":
    # Example queries
    route_query("Which customer ordered most in Jan?")
    route_query("Find similar documents using vector search.")
    route_query("Show all entities in the graph.")
    route_query("Who works at Microsoft?")
    route_query("Who works at Google?") 