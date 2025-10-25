import anthropic

def count_tokens(model: str, messages: list[dict]) -> int:
    """Counts the number of tokens in a list of messages.
    
    Args:
        model (str): The model name.
        messages (list[dict]): A list of messages, where each message is a dict
            with 'role' and 'content' keys.

    Returns:
        int: The total number of tokens in the messages.
    """
    return anthropic.Anthropic().messages.count_tokens(
        model=model,
        messages=messages
    ).input_tokens
