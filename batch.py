import os
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request

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

def get_message_batches(model: str, prompt_template: str, chunk_folder: str) -> list[Request]:
    """Create message batches for all chunk files in a folder.

    Args:
        model (str): The model to use for message generation.
        prompt_template (str): The prompt template with a placeholder for content.
        chunk_folder (str): The folder containing chunk files.

    Returns:
        list[Request]: A list of batch requests.
    """
    batches = []
    if os.path.isdir(chunk_folder):
        for fname in sorted(os.listdir(chunk_folder)):
            if not fname.lower().endswith('.md'):
                continue

            chunk_path = os.path.join(chunk_folder, fname)
            with open(chunk_path, 'r', encoding='utf-8') as cf:
                chunk_text = cf.read()

            full_prompt = prompt_template.replace("{{content}}", chunk_text)
            messages = [{"role": "user", "content": full_prompt}]

            base_part, idx_part_ext = fname.rsplit('_chunk_', 1)
            base_part = base_part.rsplit(" ", 1)[1]
            idx_part = idx_part_ext.split('.', 1)[0]

            custom_id = f"{base_part}_{idx_part}"
            print(f"Created batch: custom_id={custom_id}, file={fname}")

            batch_request = create_message_batch(
                model=model,
                prompt=messages,
                custom_id=custom_id
            )
            batches.append(batch_request)
    return batches
