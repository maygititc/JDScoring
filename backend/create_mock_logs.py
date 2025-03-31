import os
import json
import random
from datetime import datetime, timedelta

# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.getcwd(), "logs")
os.makedirs(logs_dir, exist_ok=True)

# Current date
today = datetime.now()
date_str = today.strftime("%Y-%m-%d")

# Create mock API logs
api_log_file = os.path.join(logs_dir, f"api_{date_str}.log")

# HTTP methods
methods = ["GET", "POST", "PUT", "DELETE"]
paths = ["/api/analyze-jd", "/api/generate-questions", "/api/evaluate-answer", "/api/logs/api"]
status_codes = [200, 201, 400, 404, 500]

# Create mock API logs
with open(api_log_file, "w") as f:
    for i in range(20):
        timestamp = (today - timedelta(minutes=i*5)).strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
        method = random.choice(methods)
        path = random.choice(paths)
        status_code = random.choice(status_codes)
        duration_ms = random.uniform(50, 500)
        
        level = "INFO"
        if status_code >= 400 and status_code < 500:
            level = "WARNING"
        elif status_code >= 500:
            level = "ERROR"
        
        log_data = {
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": duration_ms
        }
        
        log_line = f'{timestamp} - interview-prep - {level} - {json.dumps(log_data)}\n'
        f.write(log_line)

print(f"Created mock API logs at {api_log_file}")

# Create mock LLM logs
llm_log_file = os.path.join(logs_dir, f"llm_{date_str}.log")

# LLM operations
operations = ["analyze_jd", "generate_questions", "evaluate_answer", "generate_answer"]
providers = ["openai", "deepseek"]

# Create mock LLM logs
with open(llm_log_file, "w") as f:
    for i in range(15):
        timestamp = (today - timedelta(minutes=i*8)).strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
        operation = random.choice(operations)
        provider = random.choice(providers)
        duration_ms = random.uniform(500, 3000)
        
        log_data = {
            "operation": operation,
            "provider": provider,
            "duration_ms": duration_ms
        }
        
        log_line = f'{timestamp} - interview-prep - INFO - {json.dumps(log_data)}\n'
        f.write(log_line)

print(f"Created mock LLM logs at {llm_log_file}")

# Create mock app logs
app_log_file = os.path.join(logs_dir, f"app_{date_str}.log")

# App messages
messages = [
    "Application started",
    "User submitted job description",
    "Generated 5 questions",
    "User answered question",
    "Evaluation completed",
    "Error processing request"
]

# Create mock app logs
with open(app_log_file, "w") as f:
    for i in range(25):
        timestamp = (today - timedelta(minutes=i*3)).strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
        message = random.choice(messages)
        
        level = "INFO"
        if "Error" in message:
            level = "ERROR"
        
        log_line = f'{timestamp} - interview-prep - {level} - {message}\n'
        f.write(log_line)

print(f"Created mock app logs at {app_log_file}")

print("Mock logs created successfully!") 