from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import router
from app.services.jd_service import JDService
from app.services.llm_factory import create_llm_service
from app.services.logging_service import LoggingService
import os
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

app = FastAPI(
    title="JD Analyzer API",
    description="API for analyzing job descriptions and generating questions",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
@app.on_event("startup")
async def startup_event():
    # Create the LLM service using the factory
    llm_service = create_llm_service()
    
    # Create the logging service
    logging_service = LoggingService()
    
    # Store the logging service in the app state
    app.state.logging_service = logging_service
    
    # Attach the logging service to the LLM service
    if hasattr(llm_service, 'logging_service'):
        llm_service.logging_service = logging_service
    
    # Create the JD service with the LLM service
    jd_service = JDService(llm_service)
    
    # Attach the logging service to the JD service
    jd_service.logging_service = logging_service
    
    # Store the JD service in the app state
    app.state.jd_service = jd_service
    
    print(f"App initialized with LLM provider: {os.getenv('LLM_PROVIDER', 'deepseek')}")

# Add middleware to log all requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Get path and method
    path = request.url.path
    method = request.method
    
    # Try to get client IP
    forwarded_for = request.headers.get("X-Forwarded-For")
    client_ip = forwarded_for.split(",")[0] if forwarded_for else request.client.host
    
    # Check if logging service exists
    has_logger = hasattr(app.state, 'logging_service') and app.state.logging_service is not None
    
    # Log request start
    if has_logger:
        app.state.logging_service.logger.info(f"Request started: {method} {path} from {client_ip}")
    else:
        print(f"Request started: {method} {path} from {client_ip}")
    
    try:
        # Process the request
        response = await call_next(request)
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Log request completion
        if has_logger:
            app.state.logging_service.logger.info(f"Request completed: {method} {path} - Status: {response.status_code} - Duration: {duration_ms:.2f}ms")
        else:
            print(f"Request completed: {method} {path} - Status: {response.status_code} - Duration: {duration_ms:.2f}ms")
        
        return response
    except Exception as e:
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Log the error
        if has_logger:
            app.state.logging_service.logger.error(f"Request failed: {method} {path} - Error: {str(e)} - Duration: {duration_ms:.2f}ms")
        else:
            print(f"Request failed: {method} {path} - Error: {str(e)} - Duration: {duration_ms:.2f}ms")
        
        raise

# Include API routes
app.include_router(router, prefix="/api")

# Add a simple root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to JD Analyzer API"} 