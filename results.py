import os
import anthropic
from dotenv import load_dotenv
load_dotenv(override=True)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

message_batch = client.messages.batches.retrieve(
    "msgbatch_01S3ckX1CBUxw2v7oy4CsTbw",
)
print(f"Batch {message_batch.id} processing status is {message_batch.processing_status}")

# Stream results file in memory-efficient chunks, processing one at a time
for result in client.messages.batches.results(
    "msgbatch_01S3ckX1CBUxw2v7oy4CsTbw"
):
    print(result)
    match result.result.type:
        case "succeeded":
            print(f"Success! {result.custom_id}")
        case "errored":
            if result.result.error.type == "invalid_request":
                # Request body must be fixed before re-sending request
                print(f"Validation error {result.custom_id}")
            else:
                # Request can be retried directly
                print(f"Server error {result.custom_id}")
        case "expired":
            print(f"Request expired {result.custom_id}")