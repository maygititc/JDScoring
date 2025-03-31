import os

def list_files(directory):
    print(f"Listing files in {directory}:")
    for root, dirs, files in os.walk(directory):
        for file in files:
            print(f"  {os.path.join(root, file)}")

# List files in the logs directory
# logs_dir = os.path.join(os.getcwd(), "logs")
# list_files(logs_dir)

from app.services.logging_service import LoggingService
logging_service = LoggingService()
logs = logging_service.get_logs("llm", "")
print(logs)