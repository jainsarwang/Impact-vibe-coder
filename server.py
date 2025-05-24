import logging
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(filename)s - %(levelname)s - %(message)s - Line No : %(lineno)d",
    filename="app.log",
    filemode='a'
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting LangManus API server")
    uvicorn.run(
        "src.api.app:app",
        host="0.0.0.0",
        port=8080,
        reload=True,  # Always enable reload
        reload_dirs=["src"],  # Watch only the "src" directory
        log_level="info",
    )