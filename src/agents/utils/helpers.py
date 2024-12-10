import time
import random
import openai

def retry_request(func, *args, max_retries=2, **kwargs):
    base_sleep = 1  # base sleep time in seconds
    for attempt in range(max_retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Handle non-OpenAI specific exceptions
            print(f"An unexpected error occurred: {str(e)}")
            if attempt == max_retries:
                raise
            sleep_time = base_sleep * 2 ** attempt
            sleep_time += random.uniform(0, base_sleep)
            print(f"Retrying request, attempt {attempt + 1}. Waiting {sleep_time} seconds. General Error: {str(e)}")
            time.sleep(sleep_time)
    return None