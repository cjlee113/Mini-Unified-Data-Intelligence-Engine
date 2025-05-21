import os
import json

def log_feedback(query, doc_id, rating, comment, log_path='project/feedback/feedback_log.jsonl'):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    entry = {
        'query': query,
        'doc_id': doc_id,
        'rating': rating,
        'comment': comment
    }
    print("Logging feedback:", entry)  # Debug print
    with open(log_path, 'a') as f:
        f.write(json.dumps(entry) + '\n') 