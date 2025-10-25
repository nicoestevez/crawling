import os
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request
from tokens import count_tokens

def create_message_batch(model: str, prompt: list[dict], custom_id: str) -> Request:
    """Create a batch of messages for the API.

    Args:
        model (str): The model to use for message generation.
        prompt (list[dict]): The list of messages to include in the batch.
        custom_id (str): A custom ID for the batch request.

    Returns:
        Request: The constructed batch request.
    """

    return Request(
        custom_id=custom_id,
        params=MessageCreateParamsNonStreaming(
            model=model,
            messages=prompt
        )
    )
