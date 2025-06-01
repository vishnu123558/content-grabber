import os
import requests
from urllib.parse import urlparse
from tqdm import tqdm
from bs4 import BeautifulSoup
from database import insert_file_metadata
from summarizer import process_document
from datetime import datetime
from ttkthemes import ThemedTk

# Storage  Directories
STORAGE_DIR = "storage"
IMAGE_DIR = os.path.join(STORAGE_DIR, "images")
PDF_DIR = os.path.join(STORAGE_DIR, "pdfs")

os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)

def sanitize_filename(url):
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path)
    if not filename:
        filename = f"file_{hash(url)[:8]}"
    return filename

def get_file_extension(url):
    parsed = urlparse(url)
    return os.path.splitext(parsed.path)[1][1:].lower() or 'unknown'

def download_file(url, save_path, file_type):
    try:
        if not url.startswith(('http://', 'https://')):
            raise ValueError(f"Invalid URL format: {url}")

        response = requests.get(url, stream=True, timeout=15)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        with open(save_path, 'wb') as f, tqdm(
            desc=os.path.basename(save_path),
            total=total_size,
            unit='B',
            unit_scale=True,
        ) as bar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    bar.update(len(chunk))

        print(f"✅ Downloaded: {save_path}")
        insert_file_metadata(url, os.path.basename(save_path), file_type)

        if file_type == "pdf":
            summary = process_document(save_path)
            print(f"📜 Summary:\n{summary}\n")

    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")
        if os.path.exists(save_path):
            os.remove(save_path)
        raise

def save_images(image_urls, target_dir=None):
    if target_dir:
        global IMAGE_DIR
        IMAGE_DIR = target_dir
        os.makedirs(IMAGE_DIR, exist_ok=True)

    saved_files = []
    for url in image_urls:
        try:
            if os.path.exists(url) or not url.startswith(('http://', 'https://')):
                print(f"⚠️ Skipping local path or invalid URL: {url}")
                continue

            response = requests.get(url, stream=True, timeout=15)
            response.raise_for_status()
            content_type = response.headers.get('content-type', '').lower()
            ext = content_type.split('/')[-1] if 'image' in content_type else 'jpg'
            if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                ext = 'jpg'

            ext_dir = os.path.join(IMAGE_DIR, ext)
            os.makedirs(ext_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"image_{timestamp}_{len(saved_files)}.{ext}"
            save_path = os.path.join(ext_dir, filename)

            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            saved_files.append(save_path)
            print(f"✅ Saved image: {filename}")
            print(f"📂 Location: {os.path.abspath(save_path)}")
            insert_file_metadata(url, filename, "image")

        except Exception as e:
            print(f"❌ Failed to save image from {url}: {e}")
            continue

    return saved_files

def save_pdfs(pdf_urls, target_dir=None):
    if target_dir:
        global PDF_DIR
        PDF_DIR = target_dir
        os.makedirs(PDF_DIR, exist_ok=True)

    saved_files = []
    summaries = {}

    for i, url in enumerate(pdf_urls, 1):
        try:
            if not url.startswith(('http://', 'https://')):
                continue

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"document_{i}_{timestamp}.pdf"
            save_path = os.path.join(PDF_DIR, filename)

            # Download with proper headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/pdf,*/*'
            }

            response = requests.get(url, stream=True, timeout=30, headers=headers)
            response.raise_for_status()

            # Save the file
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            # Verify file was saved and has content
            if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
                saved_files.append(save_path)
                try:
                    summary = process_document(save_path)
                    if summary and not summary.startswith("⚠️"):
                        summaries[save_path] = summary
                        print(f"📝 Generated summary for {filename}")
                    else:
                        summaries[save_path] = "⚠️ No summary available"
                except Exception as e:
                    print(f"⚠️ Summary generation failed for {filename}: {e}")
                    summaries[save_path] = f"⚠️ Summary generation failed: {str(e)}"

                print(f"✅ Saved PDF: {filename}")
                insert_file_metadata(url, filename, "pdf")
            else:
                print(f"❌ Failed to save PDF: Empty or missing file")
                if os.path.exists(save_path):
                    os.remove(save_path)

        except Exception as e:
            print(f"❌ Failed to save PDF from {url}: {e}")
            if 'save_path' in locals() and os.path.exists(save_path):
                os.remove(save_path)
            continue

    return saved_files, summaries
