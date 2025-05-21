from neo4j import GraphDatabase
from dotenv import load_dotenv
import os
import logging
import re
import duckdb
import openai

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
    con = duckdb.connect()
    csv_path = "project/data/day1_structured/input/orders.csv"
    con.execute(f"CREATE OR REPLACE TABLE orders AS SELECT * FROM read_csv_auto('{csv_path}')")
    q = query.lower()
    if "ordered the most in japan" in q:
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
    elif "show all orders from japan" in q:
        result = con.execute("""
            SELECT * FROM orders WHERE country = 'Japan'
        """).fetchall()
        con.close()
        if result:
            return f"Orders from Japan: {result}"
        else:
            return "No orders found for Japan."
    elif "customers who placed orders in january" in q or "customers who ordered in january" in q:
        result = con.execute("""
            SELECT DISTINCT customer FROM orders WHERE LOWER(month) = 'january'
        """).fetchall()
        con.close()
        if result:
            customers = ', '.join(r[0] for r in result)
            return f"Customers who placed orders in January: {customers}"
        else:
            return "No customers found for January."
    elif "total amount ordered by each customer" in q:
        result = con.execute("""
            SELECT customer, SUM(amount) as total_amount FROM orders GROUP BY customer
        """).fetchall()
        con.close()
        if result:
            return "Total amount ordered by each customer: " + ', '.join(f"{r[0]}: {r[1]}" for r in result)
        else:
            return "No orders found."
    else:
        con.close()
        return f"[SQLTool] Executed SQL query: {query}"

def VectorTool(query):
    q = query.lower()
    if "similar documents" in q or "documents similar to" in q or "similarity search" in q:
        # Return mock similar documents
        return "Top similar documents: doc1, doc2, doc3"
    elif "embedding" in q:
        return "Embedding for the input text: [0.12, 0.34, 0.56, ...]"
    else:
        return f"[VectorTool] Performed vector search for: {query}"

def GraphTool(query):
    q = query.lower()
    # Who works at <Company>?
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
    # Show all entities in the graph
    elif "show all entities" in q:
        cypher = "MATCH (n) RETURN DISTINCT labels(n) AS labels, n.name AS name LIMIT 50"
        with driver.session() as session:
            result = session.run(cypher)
            entities = [f"{record['labels'][0]}: {record['name']}" for record in result if record['name']]
        return f"Entities in the graph: {', '.join(entities) if entities else 'None found'}"
    # Who acquired <Company>?
    match_acq = re.match(r"who acquired (.+)\??", query.strip(), re.IGNORECASE)
    if match_acq:
        company = match_acq.group(1).strip().rstrip('?')
        cypher = (
            "MATCH (a:Company)-[:ACQUIRED]->(b:Company) "
            "WHERE toLower(b.name) = toLower($company) "
            "RETURN a.name AS acquirer"
        )
        with driver.session() as session:
            result = session.run(cypher, company=company)
            acquirers = [record["acquirer"] for record in result]
        return f"Companies that acquired {company}: {', '.join(acquirers) if acquirers else 'None found'}"
    # Who was acquired by <Company>? / Who did <Company> acquire? / Which companies did <Company> acquire?
    match_acquired_by = re.match(r"who was acquired by (.+)\??", query.strip(), re.IGNORECASE)
    match_did_acquire = re.match(r"who did (.+) acquire\??", query.strip(), re.IGNORECASE)
    match_which_companies = re.match(r"which companies did (.+) acquire\??", query.strip(), re.IGNORECASE)
    if match_acquired_by or match_did_acquire or match_which_companies:
        if match_acquired_by:
            company = match_acquired_by.group(1).strip().rstrip('?')
        elif match_did_acquire:
            company = match_did_acquire.group(1).strip().rstrip('?')
        else:
            company = match_which_companies.group(1).strip().rstrip('?')
        cypher = (
            "MATCH (a:Company)-[:ACQUIRED]->(b:Company) "
            "WHERE toLower(a.name) = toLower($company) "
            "RETURN b.name AS acquired"
        )
        with driver.session() as session:
            result = session.run(cypher, company=company)
            acquired = [record["acquired"] for record in result]
        return f"Companies acquired by {company}: {', '.join(acquired) if acquired else 'None found'}"
    # List all people who work at <Company>
    match_people = re.match(r"list all people who work at (.+)\??", query.strip(), re.IGNORECASE)
    if match_people:
        company = match_people.group(1).strip().rstrip('?')
        cypher = (
            "MATCH (p:Person)-[:WORKS_AT]->(c:Company) "
            "WHERE toLower(c.name) = toLower($company) "
            "RETURN p.name AS name"
        )
        with driver.session() as session:
            result = session.run(cypher, company=company)
            people = [record["name"] for record in result]
        return f"People who work at {company}: {', '.join(people) if people else 'None found'}"
    # Which companies are mentioned in the documents?
    elif "companies mentioned in the documents" in q:
        cypher = (
            "MATCH (c:Company)<-[:MENTIONS]-(d:Document) "
            "RETURN DISTINCT c.name AS company"
        )
        with driver.session() as session:
            result = session.run(cypher)
            companies = [record["company"] for record in result]
        return f"Companies mentioned in documents: {', '.join(companies) if companies else 'None found'}"
    else:
        return f"[GraphTool] No logic for this query yet: {query}"

def llm_tool_router(question, openai_api_key=None):
    """Use GPT to select the tool for a given question."""
    prompt = (
        "You are a tool router. Given a user question, choose the best tool to answer it.\n"
        "Available tools:\n"
        "- SQLTool: For questions about structured data, orders, customers, amounts, etc.\n"
        "- GraphTool: For questions about relationships, entities, companies, people, acquisitions, etc.\n"
        "- VectorTool: For questions about similarity, embeddings, or finding similar documents.\n\n"
        f"Question: \"{question}\"\nTool:"
    )
    if not openai_api_key:
        openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        return None
    openai.api_key = openai_api_key
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=5,
            temperature=0
        )
        tool = response.choices[0].text.strip()
        if tool in ["SQLTool", "GraphTool", "VectorTool"]:
            return tool
    except Exception as e:
        logging.warning(f"LLM router failed: {e}")
    return None

def route_query(query, use_llm_router=True, openai_api_key=None):
    q = query.lower()
    tool = None
    tool_name = None
    if use_llm_router:
        tool_name = llm_tool_router(query, openai_api_key)
        if tool_name == "SQLTool":
            tool = SQLTool
        elif tool_name == "GraphTool":
            tool = GraphTool
        elif tool_name == "VectorTool":
            tool = VectorTool
    # Fallback to keyword routing if LLM fails
    if not tool:
        if any(word in q for word in ["order", "customer", "jan"]):
            tool = SQLTool
            tool_name = "SQLTool"
        elif any(word in q for word in ["vector", "embedding", "similarity"]):
            tool = VectorTool
            tool_name = "VectorTool"
        elif any(word in q for word in ["graph", "entity", "relationship", "works at", "work at", "people who work at", "acquire", "acquired"]):
            tool = GraphTool
            tool_name = "GraphTool"
        else:
            tool = lambda q: "[Default] No suitable tool found."
            tool_name = "None"
    logging.info(f"Input: {query}")
    logging.info(f"Tool used: {tool_name}")
    output = tool(query)
    logging.info(f"Output: {output}\n")
    return output, tool_name

if __name__ == "__main__":
    # Example queries
    route_query("Which customer ordered most in Jan?")
    route_query("Find similar documents using vector search.")
    route_query("Show all entities in the graph.")
    route_query("Who works at Microsoft?")
    route_query("Who works at Google?") 