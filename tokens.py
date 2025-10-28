from time import sleep
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
    for attempt in range(3):
        try:
            input_tokens = anthropic.Anthropic().messages.count_tokens(
                model=model,
                messages=messages
            ).input_tokens
            return input_tokens
        except anthropic.RateLimitError as e:
            print(f"Error counting tokens: {e}")
            if attempt < 2:
                print(f"Retrying {attempt + 1}/3...")
                sleep(60)
            else:
                raise e

    return input_tokens
