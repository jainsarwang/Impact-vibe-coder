"""
Server script for running the LangManus API.
"""

import logging
from dotenv import load_dotenv
import uvicorn
import sys

load_dotenv()


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(filename)s - %(levelname)s - %(message)s - Line No : %(lineno)d",
    filename="app.log",
    filemode='a'
)

# from src.service.mongodb import con

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting IVC API server")
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
