import json
from collections import Counter, defaultdict
from datetime import datetime
import os

def load_audit_log(log_path='project/feedback/query_audit_log.jsonl'):
    if not os.path.exists(log_path):
        return []
    with open(log_path, 'r') as f:
        return [json.loads(line) for line in f if line.strip()]

def query_count_per_day(logs):
    counts = Counter()
    for entry in logs:
        date = entry['timestamp'][:10]  # YYYY-MM-DD
        counts[date] += 1
    return dict(counts)

def tool_usage_stats(logs):
    counts = Counter(entry['tool_used'] for entry in logs)
    return dict(counts)

def average_query_time(logs):
    durations = [entry.get('duration') for entry in logs if entry.get('duration') is not None]
    if not durations:
        return None
    return sum(durations) / len(durations)

def get_all_metrics():
    logs = load_audit_log()
    return {
        'query_count_per_day': query_count_per_day(logs),
        'tool_usage_stats': tool_usage_stats(logs),
        'average_query_time': average_query_time(logs),
    } 