def token_count(text: str) -> int:
    """
    Count the number of tokens in a given text.
    
    Args:
        text (str): The input text to count tokens for.
        
    Returns:
        int: The number of tokens in the text.
    """
    # Split the text into words and count them
    return len(text.split())