from huggingface_hub import snapshot_download
import time

repo_id = "mistralai/Mistral-7B-Instruct-v0.1"
cache_dir = "./models/Mistral-7B-Instruct-v0.1"

max_attempts = 5
for attempt in range(max_attempts):
    try:
        path = snapshot_download(
            repo_id=repo_id,
            cache_dir=cache_dir,
            max_workers=1  # reduce parallel threads to 1
        )
        print("Download completed:", path)
        break
    except Exception as e:
        print(f"Attempt {attempt + 1} failed with error: {e}")
        if attempt < max_attempts - 1:
            print("Retrying in 10 seconds...")
            time.sleep(10)
        else:
            print("Exceeded maximum retry attempts.")
