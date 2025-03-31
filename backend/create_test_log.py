import os
from datetime import datetime
import json

# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.getcwd(), "logs")
os.makedirs(logs_dir, exist_ok=True)

# Use a specific date (2025-03-27)
date_str = "2025-03-27"
date_obj = datetime.strptime(date_str, "%Y-%m-%d")
date_formatted_compact = date_obj.strftime("%Y%m%d")

# Create a test log file for API logs
api_log_file = os.path.join(logs_dir, f"api_{date_str}.log")

# Create a simple log entry
api_log_entries = [
    f'{date_str} 12:34:56,789 - interview-prep - INFO - {{"method": "GET", "path": "/api/test", "status_code": 200, "duration_ms": 123.45}}\n',
    f'{date_str} 12:35:56,789 - interview-prep - INFO - {{"method": "POST", "path": "/api/analyze-jd", "status_code": 200, "duration_ms": 345.67}}\n',
    f'{date_str} 12:36:56,789 - interview-prep - WARNING - {{"method": "GET", "path": "/api/logs/invalid", "status_code": 400, "duration_ms": 45.67}}\n',
    f'{date_str} 12:37:56,789 - interview-prep - ERROR - {{"method": "POST", "path": "/api/generate-questions", "status_code": 500, "duration_ms": 567.89}}\n'
]

# Write to the API log file
with open(api_log_file, "w") as f:
    for entry in api_log_entries:
        f.write(entry)

print(f"Created API log file at {api_log_file}")

# Create a test log file for LLM logs
llm_log_file = os.path.join(logs_dir, f"llm_{date_str}.log")

# Create LLM log entries
llm_log_entries = [
    f'{date_str} 12:34:56,789 - interview-prep - INFO - {{"operation": "analyze_jd", "provider": "deepseek", "duration_ms": 1234.56}}\n',
    f'{date_str} 12:35:56,789 - interview-prep - INFO - {{"operation": "generate_questions", "provider": "deepseek", "duration_ms": 2345.67}}\n',
    f'{date_str} 12:36:56,789 - interview-prep - INFO - {{"operation": "evaluate_answer", "provider": "deepseek", "duration_ms": 345.67}}\n'
]

# Write to the LLM log file
with open(llm_log_file, "w") as f:
    for entry in llm_log_entries:
        f.write(entry)

print(f"Created LLM log file at {llm_log_file}")

# Create a test log file for App logs
app_log_file = os.path.join(logs_dir, f"app_{date_formatted_compact}.log")

# Create App log entries
app_log_entries = [
    f'{date_str} 12:34:56,789 - interview-prep - INFO - Application started\n',
    f'{date_str} 12:35:56,789 - interview-prep - INFO - User submitted job description\n',
    f'{date_str} 12:36:56,789 - interview-prep - INFO - Generated 5 questions\n',
    f'{date_str} 12:37:56,789 - interview-prep - WARNING - User provided short answer\n',
    f'{date_str} 12:38:56,789 - interview-prep - ERROR - Error processing request\n'
]

# Write to the App log file
with open(app_log_file, "w") as f:
    for entry in app_log_entries:
        f.write(entry)

print(f"Created App log file at {app_log_file}")

# Create JSON log files for the old format
json_logs_dir = os.path.join(logs_dir, "json")
os.makedirs(json_logs_dir, exist_ok=True)

# Create API calls JSON log file
api_calls_json_file = os.path.join(json_logs_dir, f"api_calls_{date_formatted_compact}.json")
api_calls_json_entries = [
    {"timestamp": 1711540496, "level": "INFO", "message": "API request", "data": {"method": "GET", "path": "/api/test", "status_code": 200, "duration_ms": 123.45}},
    {"timestamp": 1711540556, "level": "INFO", "message": "API request", "data": {"method": "POST", "path": "/api/analyze-jd", "status_code": 200, "duration_ms": 345.67}},
    {"timestamp": 1711540616, "level": "WARNING", "message": "API request", "data": {"method": "GET", "path": "/api/logs/invalid", "status_code": 400, "duration_ms": 45.67}},
    {"timestamp": 1711540676, "level": "ERROR", "message": "API request", "data": {"method": "POST", "path": "/api/generate-questions", "status_code": 500, "duration_ms": 567.89}}
]

# Write to the API calls JSON log file
with open(api_calls_json_file, "w") as f:
    for entry in api_calls_json_entries:
        f.write(json.dumps(entry) + "\n")

print(f"Created API calls JSON log file at {api_calls_json_file}")

# Create deepseek API JSON log file
deepseek_api_json_file = os.path.join(json_logs_dir, f"deepseek_api_{date_formatted_compact}.json")
deepseek_api_json_entries = [
    {"timestamp": 1711540496, "level": "INFO", "message": "LLM operation", "data": {"operation": "analyze_jd", "provider": "deepseek", "duration_ms": 1234.56}},
    {"timestamp": 1711540556, "level": "INFO", "message": "LLM operation", "data": {"operation": "generate_questions", "provider": "deepseek", "duration_ms": 2345.67}},
    {"timestamp": 1711540616, "level": "INFO", "message": "LLM operation", "data": {"operation": "evaluate_answer", "provider": "deepseek", "duration_ms": 345.67}}
]

# Write to the deepseek API JSON log file
with open(deepseek_api_json_file, "w") as f:
    for entry in deepseek_api_json_entries:
        f.write(json.dumps(entry) + "\n")

print(f"Created deepseek API JSON log file at {deepseek_api_json_file}")

# Create user interactions JSON log file
user_interactions_json_file = os.path.join(json_logs_dir, f"user_interactions_{date_formatted_compact}.json")
user_interactions_json_entries = [
    {"timestamp": 1711540496, "level": "INFO", "message": "Application started"},
    {"timestamp": 1711540556, "level": "INFO", "message": "User submitted job description"},
    {"timestamp": 1711540616, "level": "INFO", "message": "Generated 5 questions"},
    {"timestamp": 1711540676, "level": "WARNING", "message": "User provided short answer"},
    {"timestamp": 1711540736, "level": "ERROR", "message": "Error processing request"}
]

# Write to the user interactions JSON log file
with open(user_interactions_json_file, "w") as f:
    for entry in user_interactions_json_entries:
        f.write(json.dumps(entry) + "\n")

print(f"Created user interactions JSON log file at {user_interactions_json_file}")

print("Test log files created successfully!") 