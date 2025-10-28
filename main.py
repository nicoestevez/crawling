import os
from anthropic import Anthropic
from dotenv import load_dotenv
from batch import get_message_batches 
from chunks import create_chunked_files
load_dotenv(override=True)

FOLDER_NAME = "docs"
PROMPT_FILE = "prompt.md"
MODEL = "claude-sonnet-4-5"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FOLDER_PATH = os.path.join(CURRENT_DIR, FOLDER_NAME)
CHUNKS_DIR = os.path.join(CURRENT_DIR, "chunks")
CONTEXT_WINDOW = 6500

client = Anthropic(api_key=ANTHROPIC_API_KEY)

if __name__ == "__main__":
    with open(os.path.join(CURRENT_DIR, PROMPT_FILE), 'r', encoding='utf-8') as prompt_file:
        prompt_template = prompt_file.read()

    create_chunked_files(
        prompt_template=prompt_template,
        documents_folder=FOLDER_PATH,
        chunks_folder=CHUNKS_DIR,
        model=MODEL,
        context_window=CONTEXT_WINDOW
    )

    batches = get_message_batches(
        model=MODEL,
        prompt_template=prompt_template,
        chunk_folder=CHUNKS_DIR
    )

    message_batch = client.messages.batches.create(
        requests=batches
    )

    with open(os.path.join(CURRENT_DIR, "message_batch_id.txt"), "a", encoding='utf-8') as mb_file:
        mb_file.write(f"{message_batch.id}\n")
