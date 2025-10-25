import os
from tokens import count_tokens

def chunk_file_content(content: str, prompt_template: str, model: str, max_tokens: int) -> list[str]:
    """Split `content` into chunks so that when inserted into the prompt template
    and wrapped as a single user message, the token count does not exceed max_tokens.

    This is a greedy word-based splitter: it accumulates words until adding the next
    word would push the token count over the limit, then starts a new chunk.
    
    Args:
        content (str): The full text content to be chunked.
        prompt_template (str): The prompt template with a placeholder for content.
        model (str): The model name for token counting.
        max_tokens (int): The maximum allowed tokens per chunk.
        
    Returns:
        list[str]: A list of text chunks.
    """
    words = content.split()
    chunks = []
    total_words = len(words)

    prompt_word_count = len(prompt_template.split())
    max_candidate_words = max(1, int(max_tokens * 5) - prompt_word_count)

    idx = 0
    while idx < total_words:
        tentative_end = min(total_words, idx + max_candidate_words)

        candidate_words = words[idx:tentative_end]
        candidate_text = ' '.join(candidate_words)
        full_prompt = prompt_template.replace("{{content}}", candidate_text)
        messages = [{"role": "user", "content": full_prompt}]

        t = count_tokens(model, messages)

        if t <= max_tokens:
            # Candidate fits. Try to expand further (exponential then binary) to reduce number of chunks
            lower_bound = tentative_end
            higher_bound = min(total_words, tentative_end * 2)
            # Expand exponentially to find an upper bound (limited by total_words)
            while lower_bound < higher_bound:
                try_words = words[idx:higher_bound]
                try_text = prompt_template.replace("{{content}}", ' '.join(try_words))
                t_try = count_tokens(model, [{"role": "user", "content": try_text}])

                if t_try <= max_tokens:
                    lower_bound = higher_bound
                    higher_bound = min(total_words, higher_bound * 2)
                    if lower_bound == total_words:
                        break
                else:
                    break

            left = lower_bound
            right = min(total_words, higher_bound)
            best = left
            while left < right:
                mid = (left + right + 1) // 2
                mid_text = prompt_template.replace("{{content}}", ' '.join(words[idx:mid]))
                t_mid = count_tokens(model, [{"role": "user", "content": mid_text}])
                if t_mid <= max_tokens:
                    best = mid
                    left = mid
                else:
                    right = mid - 1

            end = max(idx + 1, best)
            chunks.append(' '.join(words[idx:end]))
            idx = end
        else:
            left = idx + 1
            right = tentative_end
            best = left
            while left <= right:
                mid = (left + right) // 2
                mid_text = prompt_template.replace("{{content}}", ' '.join(words[idx:mid]))
                t_mid = count_tokens(model, [{"role": "user", "content": mid_text}])
                if t_mid <= max_tokens:
                    best = mid
                    left = mid + 1
                else:
                    right = mid - 1

            if best <= idx:
                best = idx + 1

            chunks.append(' '.join(words[idx:best]))
            idx = best

    return chunks

def create_chunk_folder(folder_path: str) -> None:
    """Create a 'chunks' subfolder within the specified folder path.

    Args:
        folder_path (str): The path where the 'chunks' folder should be created.
    """

    os.makedirs(folder_path, exist_ok=True)

def create_chunked_files(prompt_template: str, documents_folder: str, chunks_folder: str, model: str, context_window: int) -> None:
    """Read markdown files from documents_folder, chunk their content,
    and save the chunks into chunks_folder.

    Args:
        prompt_template (str): The prompt template with a placeholder for content.
        documents_folder (str): The folder containing markdown files to be chunked.
        chunks_folder (str): The folder where chunked files will be saved.
        model (str): The model name for token counting.
        context_window (int): The maximum allowed tokens per chunk.
    """

    create_chunk_folder(chunks_folder)

    files = [f for f in os.listdir(documents_folder) if f.endswith('.md')]

    for file_name in files:
        file_path = os.path.join(documents_folder, file_name)
        with open(file_path, 'r', encoding='utf-8') as fh:
            content = fh.read()

        chunks = chunk_file_content(content, prompt_template, model, context_window)

        print(f"File: {file_name} -> {len(chunks)} chunk(s)")

        base_name = os.path.splitext(file_name)[0]

        for i, chunk in enumerate(chunks, start=1):
            chunk_filename = f"{base_name}_chunk_{i}.md"
            chunk_path = os.path.join(chunks_folder, chunk_filename)

            with open(chunk_path, 'w', encoding='utf-8') as chunk_file:
                chunk_file.write(chunk)

            full_prompt = prompt_template.replace("{{content}}", chunk)
            messages = [{"role": "user", "content": full_prompt}]
            tok = count_tokens(model, messages)
            print(f"  Chunk {i}: {tok} tokens -> saved as {chunk_filename}")
