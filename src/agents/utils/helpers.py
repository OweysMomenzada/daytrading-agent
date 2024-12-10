import time
import random
from openai.error import OpenAIError

def retry_request(func, *args, max_retries=2, **kwargs):
    base_sleep = 1
    for attempt in range(max_retries + 1):
        try:
            return func(*args, **kwargs)
        except OpenAIError as e:
            if e.status_code != 500 or attempt == max_retries:
                raise
            sleep_time = base_sleep * 2 ** attempt  # exponential backoff
            sleep_time += random.uniform(0, base_sleep)  # adding some jitter
            time.sleep(sleep_time)
            print(f"Retrying request, attempt {attempt + 1}")
    return None