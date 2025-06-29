from google.genai import types

SELECTED_MODEL = "gemini-2.5-pro-preview-05-06"
REACT_FILE_STORAGE_PATH = 'projects'
ZIPPED_FILE_SOURCE_FOLDER_PATH= 'projects'
ZIPPED_FILE_EXPORT_STORAGE_PATH = 'project_zips'
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}


safety_settings = [
    types.SafetySetting(
        category="HARM_CATEGORY_DANGEROUS_CONTENT",
        threshold="BLOCK_ONLY_HIGH",
    ),
]