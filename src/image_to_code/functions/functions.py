#Loading Constants
from ..constants import (SELECTED_MODEL,
                        safety_settings)

#Loading Prompts
from ..prompts.prompts import (LAYOUT_ANALYSIS_PROMPT,
    LAYOUT_ANALYSIS_SYSTEM_PROMPT,
    COMPONENT_IDENTIFICATION_PROMPT,
    COMPONENT_IDENTIFICATION_SYSTEM_PROMPT,
    STYLING_ANALYSIS_PROMPT,
    STYLING_ANALYSIS_SYSTEM_PROMPT,
    ADD_TRANSITIONS_REACT_SYSTEM_PROMPT,
    CODE_GENERATION_SYSTEM_PROMPT_REACT,
    REFINE_REACT_CODE_SYSTEM_PROMPT,
)

#Importing Libraries
import os
import re
import json
from PIL import Image
from io import BytesIO
from google import genai
from dotenv import load_dotenv
from google.genai import types
from typing import Dict, Any
from typing import Dict,Any
from PIL import Image
from typing import Dict, Any


#Loading Environment Variables
load_dotenv()

#Google API Key
# GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_API_KEY = "AIzaSyAFQuKUbXKt88PkFBo2NaTPAUbu3sQwWTw"


#Initializing Client
client = genai.Client(api_key=GOOGLE_API_KEY)

#Parsing JSON output : Helper Function
def parse_json(json_output: str):
    # Parsing out the markdown fencing
    lines = json_output.splitlines()
    for i, line in enumerate(lines):
        if line == "```json":
            json_output = "\n".join(lines[i+1:])  # Remove everything before "```json"
            json_output = json_output.split("```")[0]  # Remove everything after the closing "```"
            break  # Exit the loop once "```json" is found
    json_output = json_output.replace('\n','')
    return json_output


#Parsing Backticks : Helper Function
def parse_backticks(json_output: str):
    # Parsing out the markdown fencing
    lines = json_output.splitlines()
    for i, line in enumerate(lines):
        if '``' in line :
            json_output = "\n".join(lines[i+1:])  # Remove everything before "```json"
            json_output = json_output.split("```")[0]  # Remove everything after the closing "```"
            break  # Exit the loop once "```json" is found
    json_output = json_output.replace('\n','')
    return json_output    


#Image to Response Generation
def image_to_response(
    image_path: str,
    system_instructions: str = None,
    model_name: str = SELECTED_MODEL,
    prompt: str = "What is this image about"
) -> str:
    """
Generates a text response from a vision model based on an input image.

This function takes an image path, processes the image, and sends it to a specified
vision model along with a prompt and optional system instructions. The model generates
a textual response describing or analyzing the image content.

Args:
    default_input_image_path (str): Path to the input image file. Defaults to 
        DEFAULT_INPUT_IMAGE_PATH.
    system_instructions (str, optional): Additional instructions or context for the 
        model. These act as system-level prompts guiding the model's behavior.
    model_name (str): Name of the vision model to use for generation. Defaults to 
        SELECTED_MODEL.
    prompt (str): The main prompt/question to ask about the image. Defaults to 
        "What is this image about".

Returns:
    str: The generated text response from the model describing or analyzing the image.

Example:
    >>> response = image_to_response(
    ...     default_input_image_path="path/to/image.jpg",
    ...     prompt="Describe the main objects in this image"
    ... )
    >>> print(response)
    "The image shows a black cat sitting on a windowsill..."

Notes:
    - The image is automatically resized to a maximum of 1024x1024 pixels while 
        maintaining aspect ratio.
    - The function uses LANCZOS resampling for high-quality downscaling.
    - Default safety settings and temperature (0.5) are applied to the model's 
        generation config.
"""
    # Load and preprocess image
    im = Image.open(BytesIO(open(image_path, "rb").read()))
    im.thumbnail([1024, 1024], Image.Resampling.LANCZOS)

    # Run model to find bounding boxes
    response = client.models.generate_content(
        model=model_name,
        contents=[prompt, im],
        config=types.GenerateContentConfig(
            system_instruction=system_instructions,
            temperature=0.5,
            safety_settings=safety_settings,
        )
    )

    return response.text
    # return parse_json(response.text)  # Recommended to uncomment this for clean JSON output


#Function to get configured response from particular models
def prompt_to_response(query,model=SELECTED_MODEL,temperature = 1.0,
                               top_p = 1.0,
                               system_prompt_given=''):
    
    """
    Generates a configured response from a specified language model based on the input query.

    This function sends a query to a specified language model with customizable generation
    parameters and returns the model's response. It allows control over various aspects of
    the text generation process.

    Args:
        query (str): The input text/prompt to send to the model.
        model (str): The name/identifier of the language model to use.
        temperature (float, optional): Controls randomness in generation. 
            Higher values (closer to 1.0) make output more random, lower values make it 
            more deterministic. Defaults to 1.0.
        top_p (float, optional): Nucleus sampling parameter controlling diversity. 
            Defaults to 1.0 (no filtering).
        max_completion_tokens (int, optional): Maximum number of tokens to generate in 
            the response. Defaults to 1024.
        system_prompt_given (str, optional): System-level instructions that guide the 
            model's behavior. Defaults to empty string.

    Returns:
        The raw response object from the model's generate_content method, which typically
        contains the generated text and other metadata.

    Example:
        >>> response = return_configured_response(
        ...     query="Explain quantum computing in simple terms",
        ...     model="gemini-pro",
        ...     temperature=0.7,
        ...     max_completion_tokens=500
        ... )
        >>> print(response.text)

    Notes:
        - The function uses the client.models.generate_content API for generation
        - Default parameters are set for balanced generation (temperature=1.0, top_p=1.0)
        - The top_p parameter is currently not used in the implementation but remains
          in the interface for future compatibility
    """
    

    response = client.models.generate_content(
        model = SELECTED_MODEL,
        contents = [query],
        config = types.GenerateContentConfig(
            temperature = temperature,
            system_instruction = system_prompt_given
        )
    )
    
    return response


#Get Coordinates
bounding_box_prompt = "Detect the 2d bounding boxes for the HTML components such as images , texts , links dividers any of them"

bounding_box_system_instructions = """
    Return bounding boxes as a JSON array . Never return masks or code fencing. Limit to 25 objects.
    If an object is present multiple times, name them according to their unique characteristic (colors, size, position, unique characteristics, etc..).
      """

def get_coordinates(
    image_path: str,
    bounding_box_system_instructions: str = bounding_box_system_instructions,
    model_name: str = SELECTED_MODEL,
    bounding_box_prompt: str = bounding_box_prompt
) -> str:
    """Generates bounding box coordinates for objects in an image using a specified model.

    Processes an input image, resizes it, and uses a generative AI model to detect objects
    and return their bounding box coordinates in JSON format.

    Args:
        default_input_image_path: Path to the input image file. Defaults to DEFAULT_INPUT_IMAGE_PATH.
        bounding_box_system_instructions: System instructions for the bounding box detection task.
        model_name: Name of the generative AI model to use. Defaults to SELECTED_MODEL.
        bounding_box_prompt: Prompt instructing the model to generate bounding boxes.

    Returns:
        str: JSON-formatted string containing bounding box coordinates. The response is typically
             in markdown format (```json ... ```) which needs parsing.

    Example:
        >>> coords = get_coordinates("image.jpg")
        >>> print(coords)
        ```json
        {"objects": [{"label": "dog", "box2d": [x1, y1, x2, y2]}]}
        ```

    Note:
        - The image is automatically resized to max 1024x1024 pixels using LANCZOS resampling.
        - Uses predefined safety_settings for content generation.
        - The actual return should probably be parsed with parse_json() (currently commented out).
    """
    # Load and preprocess image
    im = Image.open(BytesIO(open(image_path, "rb").read()))
    im.thumbnail([1024, 1024], Image.Resampling.LANCZOS)

    # Run model to find bounding boxes
    response = client.models.generate_content(
        model=model_name,
        contents=[bounding_box_prompt, im],
        config=types.GenerateContentConfig(
            system_instruction=bounding_box_system_instructions,
            temperature=0.5,
            safety_settings=safety_settings,
        )
    )

    return response.text
    # return parse_json(response.text)  # Recommended to uncomment this for clean JSON output


#Analyze Layout Structure
def analyze_layout_structure(
    image_path: str = None,
    model_name: str = SELECTED_MODEL
) -> Dict[str, Any]:
    """
    Analyzes the overall layout structure of a website screenshot.
    
    Returns:
        Dict containing layout analysis with sections, positioning, and structure info
    """
    if not image_path:
        image_path
    if not model_name:
        model_name = SELECTED_MODEL
        
    response = image_to_response(
        image_path=image_path,
        system_instructions=LAYOUT_ANALYSIS_SYSTEM_PROMPT,
        model_name=model_name,
        prompt=LAYOUT_ANALYSIS_PROMPT
    )
    
    return parse_json(response)


#Identify Components with Coordinates
def identify_components_with_coordinates(
    image_path: str = None,
    coordinates_data: str = None,
    model_name: str = SELECTED_MODEL
) -> Dict[str, Any]:
    """
    Identifies UI components using both visual analysis and bounding box coordinates.
    
    Args:
        coordinates_data: JSON string from get_coordinates function
        
    Returns:
        Dict containing detailed component analysis
    """
    if not image_path:
        image_path
    if not model_name:
        model_name = SELECTED_MODEL
    
    enhanced_prompt = f"""
    {COMPONENT_IDENTIFICATION_PROMPT}
    
    Additional context - Bounding box coordinates for elements:
    {coordinates_data}
    
    Use these coordinates to enhance your component identification and positioning analysis.
    """
    
    response = image_to_response(
        image_path=image_path,
        system_instructions=COMPONENT_IDENTIFICATION_SYSTEM_PROMPT,
        model_name=model_name,
        prompt=enhanced_prompt
    )
    
    return parse_json(response)
    # return response


#Extract Styling Specifications
def extract_styling_specifications(
    image_path: str = None,
    model_name: str = SELECTED_MODEL
) -> Dict[str, Any]:
    """
    Extracts detailed styling information for CSS generation.
    
    Returns:
        Dict containing color palette, typography, spacing, and visual effects
    """
    if not image_path:
        image_path
    if not model_name:
        model_name = SELECTED_MODEL
        
    response = image_to_response(
        image_path=image_path,
        system_instructions=STYLING_ANALYSIS_SYSTEM_PROMPT,
        model_name=model_name,
        prompt=STYLING_ANALYSIS_PROMPT
    )
    
    return parse_json(response)


#Generate Frontend Code
def generate_frontend_code(
    layout_data: Dict[str, Any],
    components_data: Dict[str, Any],
    styling_data: Dict[str, Any],
    model_name: str = SELECTED_MODEL
) -> str:
    """
    Generates complete HTML/CSS/JS code based on analysis data.
    
    Args:
        layout_data: Layout structure analysis
        components_data: Component identification results
        styling_data: Styling specifications
        
    Returns:
        Complete frontend code as string
    """
    if not model_name:
        model_name = SELECTED_MODEL
    
    model_name = SELECTED_MODEL
    
    code_prompt = f"""
    Generate complete, production-ready HTML/CSS/JS code based on this analysis:
    
    LAYOUT STRUCTURE:
    {json.dumps(layout_data, indent=2)}
    
    COMPONENTS IDENTIFIED:
    {json.dumps(components_data, indent=2)}
    
    STYLING SPECIFICATIONS:
    {json.dumps(styling_data, indent=2)}
    
    Requirements:
    1. Create a single HTML file with embedded CSS and JS
    2. Use semantic HTML5 elements
    3. Implement responsive design with CSS Grid/Flexbox
    4. Include all identified components with accurate styling
    5. Add basic interactivity where appropriate
    6. Use modern CSS practices (custom properties, etc.)
    7. Ensure accessibility (ARIA labels, semantic structure)
    
    Provide clean, well-commented code that accurately represents the original design.
    """
    
    response = prompt_to_response(
        query=code_prompt,
        model=model_name,
        temperature=0.3,
        # system_prompt_given=CODE_GENERATION_SYSTEM_PROMPT
        system_prompt_given=CODE_GENERATION_SYSTEM_PROMPT_REACT
    )
    
    return response.text


#Refine and Optimize the Code
def refine_and_optimize_code(code: str, model_name: str = None) -> str:
    """
    Refines generated code for better quality and optimization.
    """
    if not model_name:
        model_name = SELECTED_MODEL
        
    refinement_prompt = f"""
    Review and optimize this frontend code:
    
    {code}
    
    Improvements to make:
    1. Optimize CSS for better performance
    2. Ensure cross-browser compatibility
    3. Improve accessibility features
    4. Add responsive breakpoints if missing
    5. Clean up redundant code
    6. Add helpful comments
    7. Ensure semantic HTML structure
    8. ONLY GIVE THE CODE DO NOT GIVE ANYTHING ELSE.
    9. REMEMBER THIS HTML CSS JS CODE IS SINGLE FILE ONLY.
    Return the improved, production-ready code.
    """
    
    response = prompt_to_response(
        query=refinement_prompt,
        model=model_name,
        temperature=0.2,
        # max_completion_tokens=4000,
        # system_prompt_given="You are a senior frontend developer focused on code quality, performance, and best practices."
        system_prompt_given=REFINE_REACT_CODE_SYSTEM_PROMPT
    )
    
    return (response.text)


#Transitions
def transition_added_code(code: str, model_name: str = None) -> str:
    """
    Refines generated code for by adding Transitions.
    """
    if not model_name:
        model_name = SELECTED_MODEL
        
    
    adding_transitions_prompt = f"""
    Please analyze the following HTML/CSS/JS code and enhance it by adding cool transition effects and animations. Make the interface more engaging and interactive while maintaining functionality. Return the complete single-file code with your improvements.
    Requirements:

    Add smooth transitions for hover effects, page loads, and user interactions
    Include modern CSS animations (fade-ins, slide-ins, scale effects, etc.)
    Enhance button clicks, form interactions, and navigation elements
    Use CSS transforms, keyframes, and transition properties
    Ensure animations are smooth (60fps) and not overwhelming
    Maintain the original functionality while improving user experience

    Code to enhance:
    {code}
    """
    
    response = prompt_to_response(
        query=adding_transitions_prompt,
        model=model_name,
        temperature=0.2,
        # max_completion_tokens=4000,
        # system_prompt_given="You are a senior frontend developer focused on code quality, performance, and best practices."
        system_prompt_given= ADD_TRANSITIONS_REACT_SYSTEM_PROMPT
    )
    
    return (response.text)


#REACT FUNCTIONS BELOW 
def parse_llm_output_to_files(llm_output: str) -> Dict[str, str]:
    """
    Parses the LLM's output string into a dictionary of
    {filepath: file_content}.
    """
    # Remove markdown backticks if present
    if llm_output.startswith("```") and llm_output.endswith("```"):
        llm_output = llm_output[3:-3]
        if llm_output.startswith("javascript") or llm_output.startswith("jsx"): # common mistake
            llm_output = llm_output.split("\n", 1)[1]


    files = {}
    current_file_path = None
    current_file_content = []

    for line in llm_output.splitlines():
        # Regex to find lines like "// FILE: src/App.jsx" or "# FILE: src/App.jsx"
        match = re.match(r"^(?://|#)\s*FILE:\s*(.+)$", line.strip())
        if match:
            if current_file_path and current_file_content:
                files[current_file_path] = "\n".join(current_file_content).strip()
            current_file_path = match.group(1).strip()
            current_file_content = []
        elif current_file_path is not None: # Only append if we are "inside" a file block
            current_file_content.append(line)

    if current_file_path and current_file_content: # Add the last file
        files[current_file_path] = "\n".join(current_file_content).strip()
    
    # If no FILE markers were found, assume it's a single file (e.g. App.jsx)
    # This is a fallback, ideally the LLM follows the FILE: instruction
    if not files and llm_output.strip():
         # Try to infer a common main file name or use a default
        if "App.jsx" in llm_output or "App.js" in llm_output:
             files["src/App.jsx"] = llm_output.strip() # Default path
        else:
             files["output.jsx"] = llm_output.strip() # Generic fallback

    return files


def save_files_to_disk(files_dict: Dict[str, str], output_dir: str = "react_output"):
    """
    Saves the files from the dictionary to disk.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file_path, content in files_dict.items():
        # Sanitize file_path to prevent directory traversal issues, though LLM should provide relative paths
        # For simplicity, we assume paths are like 'src/components/Button.jsx'
        full_path = os.path.join(output_dir, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Saved: {full_path}")


def generate_react_code(
    layout_data: Dict[str, Any],
    components_data: Dict[str, Any],
    styling_data: Dict[str, Any],
    model_name: str = SELECTED_MODEL
) -> str: # This will return a string containing all file contents
    if not model_name:
        model_name = SELECTED_MODEL

    code_prompt = f"""
    Generate a React application based on this analysis:

    LAYOUT STRUCTURE:
    {json.dumps(layout_data, indent=2)}

    COMPONENTS IDENTIFIED:
    {json.dumps(components_data, indent=2)}

    STYLING SPECIFICATIONS:
    {json.dumps(styling_data, indent=2)}

    Follow the React development guidelines provided in the system prompt.
    Ensure you provide the file path and name before each file's content.
    """

    response = prompt_to_response(
        query=code_prompt,
        model=model_name,
        temperature=0.3, # Adjust as needed
        system_prompt_given=CODE_GENERATION_SYSTEM_PROMPT_REACT
    )
    return response.text


def refine_react_code(code_bundle: str, model_name: str = SELECTED_MODEL) -> str:
    if not model_name:
        model_name = SELECTED_MODEL

    refinement_prompt = f"""
    Review and optimize this React codebase:

    {code_bundle}

    Follow the React refinement guidelines provided in the system prompt.
    Return the improved code, maintaining the multi-file format with clear file path indicators.
    """
    response = prompt_to_response(
        query=refinement_prompt,
        model=model_name,
        temperature=0.2,
        system_prompt_given=REFINE_REACT_CODE_SYSTEM_PROMPT
    )
    return response.text


def transition_added_react_code(code_bundle: str, model_name: str = SELECTED_MODEL) -> str:
    if not model_name:
        model_name = SELECTED_MODEL

    adding_transitions_prompt = f"""
    Please analyze the following React codebase (using CSS Modules) and enhance it by adding cool transition effects and animations to the CSS.
    Make the interface more engaging and interactive while maintaining functionality.
    Return the complete set of files with your improvements, maintaining the multi-file format.

    Code to enhance:
    {code_bundle}
    """
    response = prompt_to_response(
        query=adding_transitions_prompt,
        model=model_name,
        temperature=0.2,
        system_prompt_given=ADD_TRANSITIONS_REACT_SYSTEM_PROMPT
    )
    return response.text


def remove_backticks(value: str):
    # Parsing out the markdown fencing
    lines = value.splitlines()
    filtered_lines = []
    
    for line in lines:
        if "```" not in line:
            filtered_lines.append(line)
    
    value = "\n".join(filtered_lines)
    # value = value.replace('\n','')
    return value
