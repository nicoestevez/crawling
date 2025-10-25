import os
import sys
import time
from typing import List
import anthropic
from anthropic import Anthropic
from anthropic.types.messages.batch_create_params import Request
from dotenv import load_dotenv
from batch import create_message_batch
from chunks import create_chunked_files
load_dotenv(override=True)

FOLDER_NAME = "docs"
PROMPT_FILE = "prompt.md"
MODEL = "claude-sonnet-4-5"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FOLDER_PATH = os.path.join(CURRENT_DIR, FOLDER_NAME)
CHUNKS_DIR = os.path.join(CURRENT_DIR, "chunks")
CONTEXT_WINDOW = 200000

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

    # Create batch Request objects for every chunk file in CHUNKS_DIR
    # custom_id: last word of the original base name + chunk index
    import re

    batches = []
    if os.path.isdir(CHUNKS_DIR):
        for fname in sorted(os.listdir(CHUNKS_DIR)):
            if not fname.lower().endswith('.md'):
                continue

            chunk_path = os.path.join(CHUNKS_DIR, fname)
            with open(chunk_path, 'r', encoding='utf-8') as cf:
                chunk_text = cf.read()

            # Build the full prompt for the chunk
            full_prompt = prompt_template.replace("{{content}}", chunk_text)
            messages = [{"role": "user", "content": full_prompt}]

            # Expect chunk filenames like: <base>_chunk_<index>.md
            if '_chunk_' in fname:
                base_part, idx_part_ext = fname.rsplit('_chunk_', 1)
                idx_part = idx_part_ext.split('.', 1)[0]
            else:
                # Fallback: take name without extension and use 0
                base_part = os.path.splitext(fname)[0]
                idx_part = '0'

            # Derive last word of the base part (split on common separators)
            last_word = re.split(r'[_\-\s/]+', base_part)[-1]
            custom_id = f"{last_word}_{idx_part}"

            print(f"Creating batch for file: {fname} with custom_id: {custom_id}")

            # Create the batch Request
            try:
                req = create_message_batch(MODEL, messages, custom_id)
                batches.append(req)
                print(f"Created batch: custom_id={custom_id}, file={fname}")
            except Exception as e:
                # Log and continue on error
                print(f"Failed to create batch for {fname}: {e}")
    else:
        print(f"Chunks directory '{CHUNKS_DIR}' not found or is not a directory")


    client = anthropic.Anthropic()

    client.messages.batches.create(
        requests=batches
    )