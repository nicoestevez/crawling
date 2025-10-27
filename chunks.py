import os
from tokens import count_tokens

def chunk_file_content(content: str, prompt_template: str, model: str, max_tokens: int) -> list[str]:
    """Split `content` into chunks so that when inserted into the prompt template
    and wrapped as a single user message, the token count does not exceed max_tokens.

    Optimized version with batched token counting and simplified logic.
    
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
    
    # Calculate overhead tokens from prompt template (once)
    template_overhead = count_tokens(model, [{"role": "user", "content": prompt_template.replace("{{content}}", "")}])
    effective_max_tokens = max_tokens - template_overhead
    
    # Estimate words per token (conservative: ~0.75 words/token for English)
    # This helps us make better initial guesses
    estimated_words_per_chunk = max(1, int(effective_max_tokens * 0.6))
    
    idx = 0
    while idx < total_words:
        # Start with estimated chunk size
        tentative_end = min(total_words, idx + estimated_words_per_chunk)
        
        # Build candidate and count tokens
        candidate_text = ' '.join(words[idx:tentative_end])
        full_prompt = prompt_template.replace("{{content}}", candidate_text)
        t = count_tokens(model, [{"role": "user", "content": full_prompt}])
        
        if t <= max_tokens:
            # Try to expand: use larger steps initially
            step = max(10, estimated_words_per_chunk // 4)
            
            while tentative_end < total_words:
                next_end = min(total_words, tentative_end + step)
                candidate_text = ' '.join(words[idx:next_end])
                full_prompt = prompt_template.replace("{{content}}", candidate_text)
                t_next = count_tokens(model, [{"role": "user", "content": full_prompt}])
                
                if t_next <= max_tokens:
                    tentative_end = next_end
                    t = t_next
                    # Adaptive step: if we're far from limit, keep large steps
                    if t < max_tokens * 0.8:
                        step = max(step, estimated_words_per_chunk // 4)
                    else:
                        step = max(1, step // 2)  # Reduce step as we approach limit
                else:
                    # Overshot: binary search in the gap
                    left = tentative_end
                    right = next_end - 1
                    
                    while left < right:
                        mid = (left + right + 1) // 2
                        mid_text = ' '.join(words[idx:mid])
                        mid_prompt = prompt_template.replace("{{content}}", mid_text)
                        t_mid = count_tokens(model, [{"role": "user", "content": mid_prompt}])
                        
                        if t_mid <= max_tokens:
                            left = mid
                        else:
                            right = mid - 1
                    
                    tentative_end = left
                    break
            
            chunks.append(' '.join(words[idx:tentative_end]))
            idx = tentative_end
            
        else:
            # Initial guess was too large: binary search downward
            left = idx + 1
            right = tentative_end - 1
            
            while left < right:
                mid = (left + right + 1) // 2
                mid_text = ' '.join(words[idx:mid])
                mid_prompt = prompt_template.replace("{{content}}", mid_text)
                t_mid = count_tokens(model, [{"role": "user", "content": mid_prompt}])
                
                if t_mid <= max_tokens:
                    left = mid
                else:
                    right = mid - 1
            
            chunks.append(' '.join(words[idx:left]))
            idx = left
    
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
