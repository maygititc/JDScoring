import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
import uuid

class LoggingService:
    def __init__(self):
        # Create logs directory if it doesn't exist
        self.logs_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Set up file logging
        self.log_file = os.path.join(self.logs_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("interview-prep")
        self.logger.info("Logging service initialized")
        
        # JSON logs directory
        self.json_logs_dir = os.path.join(self.logs_dir, "json")
        os.makedirs(self.json_logs_dir, exist_ok=True)
    
    def log_api_call(self, 
                    endpoint: str, 
                    request_data: Dict[str, Any], 
                    response_data: Optional[Dict[str, Any]] = None, 
                    error: Optional[str] = None,
                    duration_ms: Optional[float] = None):
        """Log an API call to both text log and JSON file"""
        
        # Generate a unique ID for this log entry
        log_id = str(uuid.uuid4())
        
        # Create log entry
        log_entry = {
            "id": log_id,
            "timestamp": datetime.now().isoformat(),
            "type": "api_call",
            "endpoint": endpoint,
            "request": self._sanitize_data(request_data),
            "response": self._sanitize_data(response_data) if response_data else None,
            "error": error,
            "duration_ms": duration_ms
        }
        
        # Log to text file
        if error:
            self.logger.error(f"API call to {endpoint} failed: {error}")
            self.logger.debug(f"Request data: {json.dumps(self._sanitize_data(request_data))}")
        else:
            self.logger.info(f"API call to {endpoint} completed in {duration_ms:.2f}ms")
            self.logger.debug(f"Request data: {json.dumps(self._sanitize_data(request_data))}")
            self.logger.debug(f"Response data: {json.dumps(self._sanitize_data(response_data)) if response_data else None}")
        
        # Log to JSON file
        self._write_json_log(log_entry, "api_calls")
    
    def log_user_interaction(self, 
                           interaction_type: str, 
                           user_data: Dict[str, Any], 
                           result: Optional[Dict[str, Any]] = None,
                           error: Optional[str] = None):
        """Log a user interaction to both text log and JSON file"""
        
        # Generate a unique ID for this log entry
        log_id = str(uuid.uuid4())
        
        # Create log entry
        log_entry = {
            "id": log_id,
            "timestamp": datetime.now().isoformat(),
            "type": "user_interaction",
            "interaction_type": interaction_type,
            "user_data": self._sanitize_data(user_data),
            "result": self._sanitize_data(result) if result else None,
            "error": error
        }
        
        # Log to text file
        if error:
            self.logger.error(f"User interaction {interaction_type} failed: {error}")
        else:
            self.logger.info(f"User interaction {interaction_type} completed")
            self.logger.debug(f"User data: {json.dumps(self._sanitize_data(user_data))}")
            self.logger.debug(f"Result: {json.dumps(self._sanitize_data(result)) if result else None}")
        
        # Log to JSON file
        self._write_json_log(log_entry, "user_interactions")
    
    def log_deepseek_api(self, 
                        operation: str, 
                        request_data: Dict[str, Any], 
                        response_data: Optional[Dict[str, Any]] = None, 
                        error: Optional[str] = None,
                        duration_ms: Optional[float] = None,
                        is_mock: bool = False):
        """Log a DeepSeek API call to both text log and JSON file"""
        
        # Generate a unique ID for this log entry
        log_id = str(uuid.uuid4())
        
        # Create log entry
        log_entry = {
            "id": log_id,
            "timestamp": datetime.now().isoformat(),
            "type": "deepseek_api",
            "operation": operation,
            "is_mock": is_mock,
            "request": self._sanitize_data(request_data),
            "response": self._sanitize_data(response_data) if response_data else None,
            "error": error,
            "duration_ms": duration_ms
        }
        
        # Log to text file
        if is_mock:
            self.logger.info(f"Mock DeepSeek API call for {operation}")
        elif error:
            self.logger.error(f"DeepSeek API call for {operation} failed: {error}")
        else:
            self.logger.info(f"DeepSeek API call for {operation} completed in {duration_ms:.2f}ms")
        
        self.logger.debug(f"Request data: {json.dumps(self._sanitize_data(request_data))}")
        if response_data:
            self.logger.debug(f"Response data: {json.dumps(self._sanitize_data(response_data))}")
        
        # Log to JSON file
        self._write_json_log(log_entry, "deepseek_api")
    
    def _sanitize_data(self, data: Any) -> Any:
        """Remove sensitive information from data before logging"""
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                # Skip API keys and other sensitive data
                if key.lower() in ["api_key", "key", "token", "password", "secret"]:
                    sanitized[key] = "***REDACTED***"
                else:
                    sanitized[key] = self._sanitize_data(value)
            return sanitized
        elif isinstance(data, list):
            return [self._sanitize_data(item) for item in data]
        else:
            return data
    
    def _write_json_log(self, log_entry: Dict[str, Any], log_type: str):
        """Write a log entry to a JSON file"""
        try:
            # Create a filename based on the date and log type
            date_str = datetime.now().strftime('%Y%m%d')
            filename = f"{log_type}_{date_str}.json"
            filepath = os.path.join(self.json_logs_dir, filename)
            
            # Append to the file
            with open(filepath, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            self.logger.error(f"Error writing JSON log: {str(e)}")
    
    def get_logs(self, log_type: str, date_str: str = None) -> List[Dict[str, Any]]:
        """
        Get logs of a specific type for a specific date
        """
        try:
            print(f"Getting logs for type={log_type}, date={date_str}")
            
            # Determine the log file path
            if date_str:
                # Parse the date string (format: YYYY-MM-DD)
                from datetime import datetime
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                date_formatted = date_obj.strftime("%Y-%m-%d")
                date_formatted_compact = date_obj.strftime("%Y%m%d")
                print(f"Parsed date: {date_formatted} (compact: {date_formatted_compact})")
            else:
                # Use today's date
                from datetime import datetime
                date_formatted = datetime.now().strftime("%Y-%m-%d")
                date_formatted_compact = datetime.now().strftime("%Y%m%d")
                print(f"Using today's date: {date_formatted} (compact: {date_formatted_compact})")
            
            # Map the new log type to the old log type
            old_log_type_map = {
                "api": "api_calls",
                "llm": "deepseek_api",
                "app": "user_interactions"
            }
            
            old_log_type = old_log_type_map.get(log_type, log_type)
            print(f"Mapped log type: {log_type} -> {old_log_type}")
            
            # Try the existing JSON log file first
            json_log_file = os.path.join(self.json_logs_dir, f"{old_log_type}_{date_formatted_compact}.json")
            print(f"Looking for JSON log file: {json_log_file}")
            
            if os.path.exists(json_log_file):
                print(f"Found JSON log file: {json_log_file}")
                # Parse the JSON log file
                logs = []
                with open(json_log_file, "r") as f:
                    for line in f:
                        try:
                            log_entry = json.loads(line.strip())
                            
                            # Convert the JSON log entry to the expected format
                            timestamp = log_entry.get("timestamp", time.time())
                            level = log_entry.get("level", "INFO")
                            message = log_entry.get("message", "")
                            data = log_entry.get("data", {})
                            
                            logs.append({
                                "timestamp": timestamp,
                                "level": level,
                                "message": message,
                                "data": data
                            })
                        except Exception as e:
                            print(f"Error parsing JSON log line: {str(e)}")
                            continue
                
                # Sort logs by timestamp (newest first)
                logs.sort(key=lambda x: x["timestamp"], reverse=True)
                
                return logs
            
            # If JSON log file doesn't exist, try the regular log file
            log_file = os.path.join(self.logs_dir, f"{log_type}_{date_formatted}.log")
            print(f"JSON log file not found, looking for regular log file: {log_file}")
            
            # Also try the compact date format for regular log files
            if not os.path.exists(log_file):
                log_file = os.path.join(self.logs_dir, f"{log_type}_{date_formatted_compact}.log")
                print(f"Regular log file not found, trying compact date format: {log_file}")
            
            # Also try the app log file which might have a different naming convention
            if not os.path.exists(log_file) and log_type == "app":
                log_file = os.path.join(self.logs_dir, f"app_{date_formatted_compact}.log")
                print(f"App log file not found, trying different naming convention: {log_file}")
            
            if not os.path.exists(log_file):
                print(f"No log files found for type={log_type}, date={date_str}")
                return []
            
            print(f"Found regular log file: {log_file}")
            
            # Parse the log file
            logs = []
            with open(json_log_file, "r") as f:
                for line in f:
                    try:
                        log_entry = json.loads(line.strip())
                        
                        # Convert the JSON log entry to the expected format
                        timestamp = log_entry.get("timestamp", time.time())
                        level = log_entry.get("level", "INFO")
                        message = log_entry.get("message", "")
                        data = log_entry.get("data", {})
                        
                        logs.append({
                            "timestamp": timestamp,
                            "level": level,
                            "message": message,
                            "data": data
                        })
                    except json.JSONDecodeError as e:
                        print(f"Error parsing JSON log line: {str(e)}")
                        continue
            
            # Sort logs by timestamp (newest first)
            logs.sort(key=lambda x: x["timestamp"], reverse=True)
            
            return logs

        except Exception as e:
            print(f"Error getting logs: {str(e)}")
            return [] 