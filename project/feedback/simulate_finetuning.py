import json
import os

feedback_path = "project/feedback/feedback_log.jsonl"

if not os.path.exists(feedback_path):
    print(f"No feedback log found at {feedback_path}.")
    exit(0)

positive_feedback = []
with open(feedback_path, "r") as f:
    for line in f:
        entry = json.loads(line)
        if entry.get("rating") == 1:
            positive_feedback.append(entry)

print(f"Found {len(positive_feedback)} positive feedback entries.\n")
for entry in positive_feedback:
    print(f"Query: {entry['query']}")
    print(f"Comment: {entry['comment']}")
    print("-" * 40)

print("\nIn a real system, these would be used to fine-tune the model or improve retrieval.") 