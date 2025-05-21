'''
Connect to Neo4j database and load spacy for entity extraction. Extracts entities from sample text
and adds doc, people, companies as nodes in Neo4j. Queries Neo4j to list people and companies mentioned.
'''
from neo4j import GraphDatabase
import spacy
import re
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")

# Connect to Neo4j
driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Sample document text
sample_text = (
    "Microsoft acquired OpenAI. Alice Brown works at Microsoft. "
    "Bob Smith joined Google last year. Carol Lee is a manager at Amazon. "
    "OpenAI partnered with DeepMind. John Doe left Apple for Meta."
    "Landon Bustos works at Google. "
)

def load_graph(tx):
    # Split text into sentences
    doc = nlp(sample_text)
    for sent in doc.sents:
        sent_text = sent.text.strip()
        if not sent_text:
            continue
        # Create a Document node for each sentence
        tx.run("MERGE (d:Document {text: $text})", text=sent_text)
        sent_doc = nlp(sent_text)
        for ent in sent_doc.ents:
            if ent.label_ == "PERSON":
                tx.run("MERGE (p:Person {name: $name})", name=ent.text)
                tx.run("MATCH (d:Document {text: $doc_text}), (p:Person {name: $name}) MERGE (d)-[:MENTIONS]->(p)", doc_text=sent_text, name=ent.text)
            elif ent.label_ == "ORG":
                tx.run("MERGE (c:Company {name: $name})", name=ent.text)
                tx.run("MATCH (d:Document {text: $doc_text}), (c:Company {name: $name}) MERGE (d)-[:MENTIONS]->(c)", doc_text=sent_text, name=ent.text)
    # Add WORKS_AT relationships for 'PERSON works at ORG' patterns in the whole text
    pattern = re.compile(r"([A-Z][a-z]+ [A-Z][a-z]+) works at ([A-Z][a-zA-Z0-9]+)")
    for match in pattern.finditer(sample_text):
        person = match.group(1)
        company = match.group(2)
        tx.run("MERGE (p:Person {name: $person})", person=person)
        tx.run("MERGE (c:Company {name: $company})", company=company)
        tx.run(
            "MATCH (p:Person {name: $person}), (c:Company {name: $company}) "
            "MERGE (p)-[:WORKS_AT]->(c)",
            person=person, company=company
        )
    # Add ACQUIRED relationships for '<Company> acquired <Company>' patterns
    pattern = re.compile(r"([A-Z][a-zA-Z0-9 ]+) acquired ([A-Z][a-zA-Z0-9 ]+)")
    for match in pattern.finditer(sample_text):
        acquirer = match.group(1).strip()
        acquired = match.group(2).strip()
        tx.run("MERGE (a:Company {name: $acquirer})", acquirer=acquirer)
        tx.run("MERGE (b:Company {name: $acquired})", acquired=acquired)
        tx.run(
            "MATCH (a:Company {name: $acquirer}), (b:Company {name: $acquired}) "
            "MERGE (a)-[:ACQUIRED]->(b)",
            acquirer=acquirer, acquired=acquired
        )

def query_graph(tx):
    # Find all documents and the entities they mention
    result = tx.run("""
        MATCH (d:Document)-[:MENTIONS]->(e)
        RETURN DISTINCT d.text AS document, labels(e)[0] AS entity_type, e.name AS entity_name
    """)
    for record in result:
        print(record)
    # Show WORKS_AT relationships
    print("\nWORKS_AT relationships:")
    result2 = tx.run("""
        MATCH (p:Person)-[:WORKS_AT]->(c:Company)
        RETURN p.name AS person, c.name AS company
    """)
    for record in result2:
        print(f"{record['person']} WORKS_AT {record['company']}")

def GraphTool(query):
    # Handle 'Who acquired <Company>?' questions
    match = re.match(r"who acquired (.+)\??", query.strip(), re.IGNORECASE)
    if match:
        acquired = match.group(1).strip().rstrip('?')
        cypher = (
            "MATCH (a:Company)-[:ACQUIRED]->(b:Company) "
            "WHERE toLower(b.name) = toLower($acquired) "
            "RETURN a.name AS acquirer"
        )
        with driver.session() as session:
            result = session.run(cypher, acquired=acquired)
            acquirers = [record["acquirer"] for record in result]
        if acquirers:
            return f"{', '.join(acquirers)} acquired {acquired}."
        else:
            return f"No acquirer found for {acquired}."
    # ... rest of your GraphTool ...

if __name__ == "__main__":
    with driver.session() as session:
        session.write_transaction(load_graph)
        print("\nDocuments and mentioned entities:")
        session.read_transaction(query_graph)

def route_query(query):
    # Route the query through your agent
    tool_name, output = GraphTool(query)
    logging.info(f"Output: {output}\n")
    return tool_name, output 