"""
Error handlers for the FastAPI application.
"""

import logging
from typing import Union
from fastapi import Request, status
from fastapi.responses import JSONResponse
from pymongo.errors import (
    PyMongoError,
    ConnectionFailure,
    OperationFailure,
    WriteError,
    DuplicateKeyError,
    ServerSelectionTimeoutError
)

# Configure logging
logger = logging.getLogger(__name__)

async def mongodb_error_handler(request: Request, exc: PyMongoError) -> JSONResponse:
    """
    Handle MongoDB-specific errors and convert them to appropriate HTTP responses.
    """
    if isinstance(exc, ConnectionFailure):
        logger.error(f"MongoDB connection error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Database connection error. Please try again later."}
        )
    
    elif isinstance(exc, ServerSelectionTimeoutError):
        logger.error(f"MongoDB server selection timeout: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Unable to connect to database server. Please try again later."}
        )
    
    elif isinstance(exc, DuplicateKeyError):
        logger.warning(f"MongoDB duplicate key error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "This record already exists."}
        )
    
    elif isinstance(exc, WriteError):
        if "Document failed validation" in str(exc):
            logger.error(f"MongoDB document validation error: {exc}")
            # Extract validation details if available
            error_details = exc.details.get('errInfo', {}).get('details', {})
            validation_errors = error_details.get('schemaRulesNotSatisfied', [])
            
            if validation_errors:
                error_message = "Validation failed: "
                for error in validation_errors:
                    if 'missingProperties' in error:
                        error_message += f"Missing required fields: {', '.join(error['missingProperties'])}. "
                    elif 'propertiesNotSatisfied' in error:
                        error_message += "Invalid field values. "
            else:
                error_message = "Document validation failed."
                
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": error_message}
            )
        else:
            logger.error(f"MongoDB write error: {exc}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Failed to write to database."}
            )
    
    elif isinstance(exc, OperationFailure):
        logger.error(f"MongoDB operation failure: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Database operation failed."}
        )
    
    # Generic MongoDB error handler
    logger.error(f"Unhandled MongoDB error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected database error occurred."}
    )

async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle any unhandled exceptions that weren't caught by specific error handlers.
    """
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred."}
    ) 