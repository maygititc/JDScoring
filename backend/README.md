## Environment Variables

This application uses environment variables for configuration, especially for API keys.

### Setting API Keys

For security reasons, API keys should be set as environment variables rather than in the `.env` file.

#### On Linux/macOS:

```bash
export DEEPSEEK_API_KEY=your_deepseek_api_key_here
export OPENAI_API_KEY=your_openai_api_key_here
```

Add these to your `~/.bashrc` or `~/.zshrc` file to make them persistent.

#### On Windows:

```cmd
set DEEPSEEK_API_KEY=your_deepseek_api_key_here
set OPENAI_API_KEY=your_openai_api_key_here
```

Or use the System Properties > Environment Variables dialog to set them permanently.

### Configuration in .env

Other configuration options can be set in the `.env` file:

```
# LLM Model Configuration
LLM_PROVIDER=deepseek  # Options: 'deepseek' or 'openai'

# Model-specific settings
DEEPSEEK_MODEL=deepseek-chat  # Default model for DeepSeek
OPENAI_MODEL=gpt-4o  # Default model for OpenAI
OPENAI_TEMPERATURE=0.7

# General settings
USE_MOCK_RESPONSES=false  # Set to true for development without API calls
``` 


docker.exe build . -t maygititc/jdbackend