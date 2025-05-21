import os
import json
from datetime import datetime

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

def log_query_audit(query, tool_used, agent_output, duration=None, log_path='project/feedback/query_audit_log.jsonl'):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    entry = {
        'query': query,
        'tool_used': tool_used,
        'agent_output': agent_output,
        'timestamp': datetime.now().isoformat(),
        'duration': duration
    }
    print("Logging query audit:", entry)  # Debug print
    with open(log_path, 'a') as f:
        f.write(json.dumps(entry) + '\n') 