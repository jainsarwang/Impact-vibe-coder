token_count_value = 0 

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

def get_token_count() -> int:
    """
    Get the current token count value.
    
    Returns:
        int: The current token count.
    """
    global token_count_value
    return token_count_value

def set_token_count(value: int) -> None:
    """
    Set the token count value.
    
    Args:
        value (int): The new token count value.
    """
    global token_count_value
    token_count_value += value