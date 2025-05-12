"""
Server script for running the LangManus API.
"""

import logging
import uvicorn
import sys

# Configure logging
logging.basicConfig(
    filename="app.log",  # Specify the log file name
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filemode="a",
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting VibeCoder API server")
    reload = True
    if sys.platform.startswith("win"):
        reload = False
    uvicorn.run(
        "src.api.app:app",
        host="0.0.0.0",
        port=8080,
        reload=reload,
        log_level="info",
    )
