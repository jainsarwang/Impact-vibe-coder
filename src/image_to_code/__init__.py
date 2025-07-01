import logging
import os
import shutil
import tempfile
import traceback # For detailed error logging
import uuid # For unique task IDs
import asyncio # For asyncio.Queue and event loop
import json

from fastapi import APIRouter, FastAPI, File, UploadFile, HTTPException, status
from fastapi.responses import FileResponse, StreamingResponse # Added StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from .constants import (
    SELECTED_MODEL,
    REACT_FILE_STORAGE_PATH,
    ZIPPED_FILE_SOURCE_FOLDER_PATH,
    ZIPPED_FILE_EXPORT_STORAGE_PATH,
    ALLOWED_EXTENSIONS,
)

# Loading Functions
from .functions.functions import (
    get_coordinates,
    remove_backticks,
    refine_react_code,
    save_files_to_disk,
    generate_react_code,
    parse_llm_output_to_files,
    analyze_layout_structure,
    transition_added_react_code,
    extract_styling_specifications,
    identify_components_with_coordinates,
)

# Loading Utility Functions
from .utils.zipped import create_zip_from_folder

from google import genai
from typing import Optional, Callable # Added Optional, Callable
from typing import Callable

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
TEMP_OUTPUT_DIR_FOR_ZIPS = tempfile.mkdtemp(prefix="project_zips_")


def call_main_image_processing_function(image_path: str, session_id: str, status_callback: Optional[Callable[[str], None]] = None) -> bool: # Modified signature
    """
    Main image processing function.
    Args:
        image_path: Path to the input image.
        status_callback: An optional callback function to report progress.
        It takes a string message as an argument.
    Returns:
        True on success, False on failure.
    """

    def _report_status(message: str):
        if status_callback:
            status_callback(message)

    try:

        # try:
        #     client = genai.Client(api_key=GOOGLE_API_KEY)
        #     _report_status("Google GenAI Client Created")
        # except Exception as e:
        #     _report_status(f"ERROR: Failed to create Google GenAI Client: {e}. Ensure GOOGLE_API_KEY is valid.")
        #     return False

        # Defining variables
        react_file_storage_path = os.path.join(REACT_FILE_STORAGE_PATH, session_id)
        os.makedirs(react_file_storage_path, exist_ok=True)

        zipped_file_source_folder_path = os.path.join(ZIPPED_FILE_SOURCE_FOLDER_PATH, session_id)

        zipped_file_export_storage_path = os.path.join(ZIPPED_FILE_EXPORT_STORAGE_PATH, f"{session_id}.zip")


        #Getting coordinates
        _report_status("Image Analysis")
        coordinates = get_coordinates(image_path=image_path)

        #Getting Layout Structure
        _report_status("Layout analysis")
        layout_structure = analyze_layout_structure(image_path=image_path,model_name=SELECTED_MODEL)

        #Getting Components with Coordinates
        _report_status("Component Identification")
        components_with_coordinates = identify_components_with_coordinates(image_path=image_path,coordinates_data=coordinates,
        model_name=SELECTED_MODEL)

        #Extracting Styling Specifications
        _report_status("Styling Extraction")
        extracted_styling_specifications = extract_styling_specifications(image_path=image_path,model_name=SELECTED_MODEL)

        #Getting Plain Front End React Code
        _report_status("Code Generation")
        plain_frontend_code = generate_react_code(layout_data=layout_structure,components_data=components_with_coordinates,styling_data=extracted_styling_specifications)

        #Refining the Plain Frontend React Code
        _report_status("Code Refinement")
        refined_frontend_code = refine_react_code(code_bundle=plain_frontend_code,
        model_name=SELECTED_MODEL)

        
        #Adding Transitions in Refined Frontend React Code
        _report_status("Transition Addition")
        transition_plain_code = transition_added_react_code(code_bundle=refined_frontend_code,
        model_name=SELECTED_MODEL)

        #Refining the Plain Transition React Code
        _report_status("Transition Refinement")
        transition_refined_code = refine_react_code(
            code_bundle=transition_plain_code,
            model_name=SELECTED_MODEL)

        _report_status("Code Parser")
        parsed_refined_transitioned_react_code = parse_llm_output_to_files(transition_refined_code)

        processed_parsed_refined_transitioned_react_code = {key: remove_backticks(value) for key, value in parsed_refined_transitioned_react_code.items()}

        _report_status(f"Saving code")
        save_files_to_disk(files_dict=processed_parsed_refined_transitioned_react_code,output_dir=react_file_storage_path)

        _report_status(f"ZIP Creation")
        create_zip_from_folder(
            folder_path_to_zip=zipped_file_source_folder_path,
            output_zip_path_with_filename=zipped_file_export_storage_path
        )

        return True
    except Exception as e:
        # Log the exception if you have a logger
        # logger.error(f"Error in main processing: {e}", exc_info=True)
        logging.error(f"ERROR in main function: {e}") # Ensure this prints to server logs
        if status_callback:
            status_callback(f"ERROR: An unexpected error occurred during processing: {str(e)}. Check server logs.")
        return False

async def generate_frontend_code(file: UploadFile = File(...), session_id: str = None):
    file_extension = os.path.splitext(file.filename)[1]

    # Check if the file extension is allowed
    if file_extension.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: '{file_extension}'. Allowed types are: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # 
    temp_dir = tempfile.mkdtemp(prefix="api_upload_")
    temp_image_path = os.path.join(temp_dir, file.filename)
    task_id = session_id

    # Save the file to the temporary directory
    try:
        with open(temp_image_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        logging.error(f"API Error: Failed to save uploaded file '{file.filename}': {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error saving uploaded file: {e}")

    # Event generator for streaming the progress
    async def event_generator():
        # Ensure temp_image_path and temp_dir are accessible in this scope
        nonlocal temp_image_path, temp_dir, task_id

        queue = asyncio.Queue()
        loop = asyncio.get_event_loop()

        def status_callback_for_main(message: str):
            # This is called from the synchronous main function (in a thread)
            # Safely put the message onto the asyncio queue
            loop.call_soon_threadsafe(queue.put_nowait, message)
            
        processing_success = False
        try:
            # Run the synchronous, long-running main function in a thread pool
            processing_task = loop.run_in_executor(
                None, # Use default thread pool executor
                call_main_image_processing_function,
                temp_image_path,
                session_id,
                status_callback_for_main # Pass the callback
            )

            while True:
                try:
                    # Wait for a message from the queue or for the task to complete
                    message = await asyncio.wait_for(queue.get(), timeout=0.2) # Short timeout
                    yield f"data: {json.dumps({'status': message})}\n\n"
                    queue.task_done()
                except asyncio.TimeoutError:
                    # Queue is empty, check if the main task is done
                    if processing_task.done():
                        break # Exit loop if main task finished
                except asyncio.CancelledError:
                    print(f"API Info: Task {task_id} event_generator cancelled.")
                    if not processing_task.done():
                        # Attempt to cancel the background task if it's still running
                        # This is best-effort; a long-blocking C extension in main_function might not be cancellable.
                        # processing_task.cancel() # Python 3.9+
                        pass # For older Python, cancellation is harder.
                    raise # Re-raise to stop the generator

            # Get the result from the main processing function
            processing_success = processing_task.result()

            if processing_success:
                zipped_file_export_storage_path = os.path.join(ZIPPED_FILE_EXPORT_STORAGE_PATH, f"{session_id}.zip")
                if not os.path.exists(zipped_file_export_storage_path):
                    err_msg = "Server error: Generated zip file not found on server despite processing success."
                    logging.error(f"API Error (task: {task_id}): {err_msg} Expected at {zipped_file_export_storage_path}")
                    yield f"data: {json.dumps({'status': 'error', 'message': err_msg})}\n\n"
                else:
                    # WORKAROUND for fixed output path in main.py:
                    # Copy the generated zip to a unique, task-specific location
                    unique_zip_filename = f"{task_id}_{os.path.basename(zipped_file_export_storage_path)}"
                    unique_zip_path = os.path.join(TEMP_OUTPUT_DIR_FOR_ZIPS, unique_zip_filename)
                    shutil.copy(zipped_file_export_storage_path, unique_zip_path)
                    
                    original_filename_for_download = f"{os.path.splitext(file.filename)[0]}_frontend.zip"
                    # task_outputs[task_id] = {
                    #     "zip_path": unique_zip_path,
                    #     "original_filename": original_filename_for_download
                    # }
                    logging.error(f"API Info (task: {task_id}): Processing complete. Zip stored at {unique_zip_path}")
            else:
                err_msg = "Failed to generate frontend code. The processing script indicated a failure."
                logging.error(f"API Error (task: {task_id}): Main function returned False.")
               
        except Exception as e:
            logging.error(f"API Error (task: {task_id}): Unexpected error during streaming/processing: {str(e)}")
            traceback.print_exc()
            # Ensure the error message is JSON serializable
            error_message_str = str(e)
            try:
                json.dumps({'message': error_message_str})
            except TypeError:
                error_message_str = "An unstringifyable error occurred."

            logging.error('Internal server error: {error_message_str}')    
        finally:
            if os.path.exists(temp_dir):
                logging.info(f"API Info (task: {task_id}): Cleaning up temporary upload directory '{temp_dir}'")
                shutil.rmtree(temp_dir)
            # Note: The original ZIPPED_FILE_EXPORT_STORAGE_PATH is NOT cleaned up here,
            # as it's overwritten by main.py. The unique_zip_path in TEMP_OUTPUT_DIR_FOR_ZIPS
            # should ideally be cleaned up after download or a timeout.

    return StreamingResponse(event_generator(), media_type="text/event-stream")

Image2CodeRouter = APIRouter()
Image2CodeRouter.add_api_route("/", generate_frontend_code, methods=["POST"], status_code=status.HTTP_200_OK)