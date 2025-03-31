import os
from app.services.deepseek_service import DeepSeekService
from app.services.openai_service import OpenAIService
from dotenv import load_dotenv

def create_llm_service():
    """
    Factory function to create the appropriate LLM service based on environment variables
    """
    # Force reload environment variables from .env file
    load_dotenv(override=True)
    
    # Get the provider from environment with explicit debug output
    llm_provider = os.getenv("LLM_PROVIDER", "deepseek").lower()
    use_mock = os.getenv("USE_MOCK_RESPONSES", "false").lower() == "true"
    
    # Print all environment variables for debugging
    print("\n--- Environment Variables ---")
    print(f"LLM_PROVIDER: {os.getenv('LLM_PROVIDER')}")
    print(f"USE_MOCK_RESPONSES: {os.getenv('USE_MOCK_RESPONSES')}")
    print(f"DEEPSEEK_MODEL: {os.getenv('DEEPSEEK_MODEL')}")
    print(f"OPENAI_MODEL: {os.getenv('OPENAI_MODEL')}")
    print("---------------------------\n")
    
    # Check if API keys are set in environment variables
    deepseek_key = os.environ.get("DEEPSEEK_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    
    print(f"Creating LLM service with provider: '{llm_provider}'")
    print(f"DeepSeek API key: {'Set' if deepseek_key else 'Not set'}")
    print(f"OpenAI API key: {'Set' if openai_key else 'Not set'}")
    print(f"Use mock responses: {use_mock}")
    
    # Create the appropriate service based on the provider
    if llm_provider == "openai":
        print("Initializing OpenAI service...")
        service = OpenAIService()
        if not openai_key and not use_mock:
            print("WARNING: Using OpenAI provider but OPENAI_API_KEY is not set")
            print("Set the OPENAI_API_KEY environment variable or enable USE_MOCK_RESPONSES")
    else:  # Default to DeepSeek
        print("Initializing DeepSeek service...")
        service = DeepSeekService()
        if not deepseek_key and not use_mock:
            print("WARNING: Using DeepSeek provider but DEEPSEEK_API_KEY is not set")
            print("Set the DEEPSEEK_API_KEY environment variable or enable USE_MOCK_RESPONSES")
    
    # Override the use_mock setting if specified in the environment
    if use_mock:
        service.use_mock = True
        print("Using mock responses as specified in environment variables")
    
    print(f"Created {type(service).__name__} successfully")
    return service 