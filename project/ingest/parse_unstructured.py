'''
Parser for unstructured data such as emails or PDFs using PyMuPDF and Python email parser, 
then extracts the text from the document and saves it to a jsonl file.
'''
import fitz
import email
from email import policy
from email.parser import BytesParser
import json
from datetime import datetime
import os

# Open the pdf file
def parse_pdf(pdf_path):
    with fitz.open(pdf_path) as f:
        text = "".join(page.get_text() for page in f)
    
    return {
        "doc_id": f"pdf_{pdf_path}",
        "source_type": "pdf",
        "title": pdf_path,
        "body": text,
        "created_at": datetime.now().strftime("%Y-%m-%d")
    }
# Parse email
def parse_email(email_path):
    with open(email_path, 'rb') as fp:
        msg = BytesParser(policy=policy.default).parse(fp)
    
    return {
        "doc_id": f"email_{email_path}",
        "source_type": "email",
        "title": msg.get("subject", ""),
        "body": msg.get_payload(),
        "created_at": datetime.now().strftime("%Y-%m-%d")
    }
# Save to jsonl
def save_to_jsonl(documents):
    """Save parsed documents to parsed_docs.jsonl in the day2 output directory"""
    output_dir = "data/test_data/day2_unstructured/output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "parsed_docs.jsonl")
    
    with open(output_path, 'w') as f:
        for doc in documents:
            f.write(json.dumps(doc) + '\n')