"""
FastAPI application for LangManus.
"""

import json
import logging
import os
from typing import Dict, List, Any, Optional, Union

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse
import asyncio
from typing import AsyncGenerator, Dict, List, Any

from src.graph import build_graph
from src.config import TEAM_MEMBERS, BROWSER_HISTORY_DIR
from src.service.workflow_service import run_agent_workflow

# Configure logging
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="LangManus API",
    description="API for LangManus LangGraph-based agent workflow",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Create the graph
graph = build_graph()


class ContentItem(BaseModel):
    type: str = Field(..., description="The type of content (text, image, etc.)")
    text: Optional[str] = Field(None, description="The text content if type is 'text'")
    image_url: Optional[str] = Field(
        None, description="The image URL if type is 'image'"
    )


class ChatMessage(BaseModel):
    role: str = Field(
        ..., description="The role of the message sender (user or assistant)"
    )
    content: Union[str, List[ContentItem]] = Field(
        ...,
        description="The content of the message, either a string or a list of content items",
    )


class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="The conversation history")
    debug: Optional[bool] = Field(False, description="Whether to enable debug logging")
    deep_thinking_mode: Optional[bool] = Field(
        False, description="Whether to enable deep thinking mode"
    )
    search_before_planning: Optional[bool] = Field(
        False, description="Whether to search before planning"
    )


@app.post("/api/chat/stream")
async def chat_endpoint(request: ChatRequest, req: Request):
    """
    Chat endpoint for LangGraph invoke.

    Args:
        request: The chat request
        req: The FastAPI request object for connection state checking

    Returns:
        The streamed response
    """
    try:
        # Convert Pydantic models to dictionaries and normalize content format
        messages = []
        for msg in request.messages:
            message_dict = {"role": msg.role}

            # Handle both string content and list of content items
            if isinstance(msg.content, str):
                message_dict["content"] = msg.content
            else:
                # For content as a list, convert to the format expected by the workflow
                content_items = []
                for item in msg.content:
                    if item.type == "text" and item.text:
                        content_items.append({"type": "text", "text": item.text})
                    elif item.type == "image" and item.image_url:
                        content_items.append(
                            {"type": "image", "image_url": item.image_url}
                        )

                message_dict["content"] = content_items

            messages.append(message_dict)

        async def event_generator():
            try:
                async for event in run_agent_workflow(
                    messages,
                    request.debug,
                    request.deep_thinking_mode,
                    request.search_before_planning,
                ):
                    # Check if client is still connected
                    if await req.is_disconnected():
                        logger.info("Client disconnected, stopping workflow")
                        break
                    yield {
                        "event": event["event"],
                        "data": json.dumps(event["data"], ensure_ascii=False),
                    }
            except asyncio.CancelledError:
                logger.info("Stream processing cancelled")
                raise

        return EventSourceResponse(
            event_generator(),
            media_type="text/event-stream",
            sep="\n",
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
async def test():
    return {"message": "API is working"}

@app.get("/api/browser_history/{filename}")
async def get_browser_history_file(filename: str):
    """
    Get a specific browser history GIF file.

    Args:
        filename: The filename of the GIF to retrieve

    Returns:
        The GIF file
    """
    try:
        file_path = os.path.join(BROWSER_HISTORY_DIR, filename)
        if not os.path.exists(file_path) or not filename.endswith(".gif"):
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(file_path, media_type="image/gif", filename=filename)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving browser history file: {e}")
        raise HTTPException(status_code=500, detail=str(e))
# """
# FastAPI application for LangManus with enhanced SSE stability.
# """

# import json
# import logging
# import os
# import asyncio
# from typing import Dict, List, Any, Optional, Union, Set

# from fastapi import FastAPI, HTTPException, Request
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import FileResponse
# from pydantic import BaseModel, Field
# from sse_starlette.sse import EventSourceResponse, ServerSentEvent

# from src.graph import build_graph
# from src.config import TEAM_MEMBERS, BROWSER_HISTORY_DIR
# from src.service.workflow_service import run_agent_workflow

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)
# logging.getLogger('sse_starlette.sse').setLevel(logging.WARNING)  # Reduce SSE lib noise

# # Connection tracking
# active_sse_connections: Set[Request] = set()

# # Create FastAPI app
# app = FastAPI(
#     title="LangManus API",
#     description="API for LangManus LangGraph-based agent workflow",
#     version="0.1.0",
# )

# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Create the graph
# graph = build_graph()

# class ContentItem(BaseModel):
#     type: str = Field(..., description="The type of content (text, image, etc.)")
#     text: Optional[str] = Field(None, description="The text content if type is 'text'")
#     image_url: Optional[str] = Field(None, description="The image URL if type is 'image'")

# class ChatMessage(BaseModel):
#     role: str = Field(..., description="The role of the message sender (user or assistant)")
#     content: Union[str, List[ContentItem]] = Field(
#         ...,
#         description="The content of the message, either a string or a list of content items",
#     )

# class ChatRequest(BaseModel):
#     messages: List[ChatMessage] = Field(..., description="The conversation history")
#     debug: Optional[bool] = Field(False, description="Whether to enable debug logging")
#     deep_thinking_mode: Optional[bool] = Field(False, description="Whether to enable deep thinking mode")
#     search_before_planning: Optional[bool] = Field(False, description="Whether to search before planning")

# @app.middleware("http")
# async def track_connections(request: Request, call_next):
#     response = await call_next(request)
#     if "/api/chat/stream" in request.url.path and request in active_sse_connections:
#         active_sse_connections.remove(request)
#     return response

# @app.on_event("shutdown")
# async def shutdown():
#     for conn in active_sse_connections:
#         try:
#             await conn.close()
#         except Exception:
#             pass
#     logger.info("Cleaned up %d SSE connections", len(active_sse_connections))

# @app.post("/api/chat/stream")
# async def chat_endpoint(request: ChatRequest, req: Request):
#     """
#     Enhanced chat endpoint with stable SSE implementation.
#     """
#     try:
#         # Convert messages to workflow format
#         messages = []
#         for msg in request.messages:
#             message_dict = {"role": msg.role}
#             if isinstance(msg.content, str):
#                 message_dict["content"] = msg.content
#             else:
#                 content_items = []
#                 for item in msg.content:
#                     if item.type == "text" and item.text:
#                         content_items.append({"type": "text", "text": item.text})
#                     elif item.type == "image" and item.image_url:
#                         content_items.append({"type": "image", "image_url": item.image_url})
#                 message_dict["content"] = content_items
#             messages.append(message_dict)

#         async def event_generator():
#             active_sse_connections.add(req)
#             try:
#                 async for event in run_agent_workflow(
#                     messages,
#                     request.debug,
#                     request.deep_thinking_mode,
#                     request.search_before_planning,
#                 ):
#                     if await req.is_disconnected():
#                         logger.info("Client disconnected during workflow")
#                         break
                        
#                     yield ServerSentEvent(
#                         event=event["event"],
#                         data=json.dumps(event["data"], ensure_ascii=False),
#                         retry=10000,  # 10 second retry
#                     )
#                     await asyncio.sleep(0.1)  # Prevent flooding
                    
#             except asyncio.CancelledError:
#                 logger.info("Stream cancelled by client")
#             except Exception as e:
#                 logger.error(f"Stream error: {str(e)}")
#                 yield ServerSentEvent(
#                     event="error",
#                     data=json.dumps({"error": str(e)})
#                 )
#             finally:
#                 if req in active_sse_connections:
#                     active_sse_connections.remove(req)

#         return EventSourceResponse(
#             event_generator(),
#             ping=15,  # Keepalive ping interval
#             ping_message_factory=lambda: ServerSentEvent(event="ping"),
#             media_type="text/event-stream",
#             timeout=30,  # Connection timeout
#         )

#     except Exception as e:
#         logger.error(f"Chat endpoint error: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/test")
# async def test():
#     return {"message": "API is working"}

# @app.get("/api/browser_history/{filename}")
# async def get_browser_history_file(filename: str):
#     """Get browser history GIF file."""
#     try:
#         file_path = os.path.join(BROWSER_HISTORY_DIR, filename)
#         if not os.path.exists(file_path) or not filename.endswith(".gif"):
#             raise HTTPException(status_code=404, detail="File not found")
#         return FileResponse(file_path, media_type="image/gif", filename=filename)
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Browser history error: {e}")
#         raise HTTPException(status_code=500, detail=str(e))