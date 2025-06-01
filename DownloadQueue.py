import os
import threading
import queue
import requests
from tqdm import tqdm
from downloader import sanitize_filename

download_queue = queue.Queue()
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_worker():
    while True:
        item = download_queue.get()
        if item is None:
            break
        url, file_type = item
        filename = sanitize_filename(url)
        download_file(url, filename, file_type)
        download_queue.task_done()

def download_file(url, filename, file_type):
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        # ... (rest of the download logic remains the same)
        print(f"✅ Downloaded: {filename} ({file_type})")
    except Exception as e:
        print(f"❌ Failed to download {filename}: {e}")

# Start worker thread
threading.Thread(target=download_worker, daemon=True).start()

def add_download(url, file_type):
    """Integrated with main downloader"""
    from downloader import sanitize_filename, get_file_extension
    filename = f"{sanitize_filename(url)}.{get_file_extension(url)}"
    print(f"📥 Adding to queue: {filename}")
    download_queue.put((url, filename, file_type))