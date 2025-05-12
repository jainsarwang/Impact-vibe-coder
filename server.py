"""
Server script for running the LangManus API.
"""

import logging
import uvicorn
import sys

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(filename)s - %(levelname)s - %(message)s",
    filename="app.log",
    filemode='a'
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting LangManus API server")
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
