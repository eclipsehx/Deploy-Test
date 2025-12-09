import os
import sys
import logging
from dotenv import load_dotenv

# Set tiktoken cache directory BEFORE any other imports that might use tiktoken
# This prevents tiktoken from trying to download files from the network
_current_file_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_current_file_dir)
os.environ['TIKTOKEN_CACHE_DIR'] = os.path.join(_project_root, 'public', 'tiktoken')

# Load environment variables from .env file
load_dotenv()

from api.logging_config import setup_logging

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

# Configure watchfiles logger to show file paths
watchfiles_logger = logging.getLogger("watchfiles.main")
watchfiles_logger.setLevel(logging.DEBUG)  # Enable DEBUG to see file paths

# Add the current directory to the path so we can import the api package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Apply watchfiles monkey patch BEFORE uvicorn import
is_development = os.environ.get("NODE_ENV") != "production"
if is_development:
    import watchfiles
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(current_dir, "logs")
    
    original_watch = watchfiles.watch
    def patched_watch(*args, **kwargs):
        # Only watch the api directory but exclude logs subdirectory
        # Add subdirectories and individual .py files (watchfiles doesn't support glob patterns)
        watch_paths = []
        for item in os.listdir(current_dir):
            item_path = os.path.join(current_dir, item)
            if os.path.isdir(item_path) and item != "logs":
                # Add subdirectories except logs
                watch_paths.append(item_path)
            elif item.endswith('.py'):
                # Add individual Python files in api root directory
                watch_paths.append(item_path)

        return original_watch(*watch_paths, **kwargs)
    watchfiles.watch = patched_watch

import uvicorn

# Check for required environment variables
required_env_vars = ['GOOGLE_API_KEY', 'OPENAI_API_KEY']
missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
if missing_vars:
    logger.warning(f"Missing environment variables: {', '.join(missing_vars)}")
    logger.warning("Some functionality may not work correctly without these variables.")

# Configure Google Generative AI
import google.generativeai as genai
from api.config import GOOGLE_API_KEY

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    logger.warning("GOOGLE_API_KEY not configured")

if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 8001))

    # Import the app here to ensure environment variables are set first
    from api.api import app

    logger.info(f"Starting Streaming API on port {port}")

    # Run the FastAPI app with uvicorn
    uvicorn.run(
        "api.api:app",
        host="0.0.0.0",
        port=port,
        reload=is_development,
        reload_excludes=["**/logs/*", "**/__pycache__/*", "**/*.pyc"] if is_development else None,
    )
