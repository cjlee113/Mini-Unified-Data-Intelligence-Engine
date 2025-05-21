import sys
import os

# Add the project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
sys.path.append(project_root)

from ingest.parse_unstructured import parse_email, parse_pdf, save_to_jsonl

# Test email parsing
email_path = "data/test_data/day2_unstructured/input/emails/test.eml"
parsed_email = parse_email(email_path)
print("Parsed Email:")
print(parsed_email)

# Test PDF parsing
pdf_path = "data/test_data/day2_unstructured/input/pdfs/test.pdf"
parsed_pdf = parse_pdf(pdf_path)
print("\nParsed PDF:")
print(parsed_pdf)

# Save both to parsed_docs.jsonl
save_to_jsonl([parsed_email, parsed_pdf])
print("\nSaved both to parsed_docs.jsonl") 