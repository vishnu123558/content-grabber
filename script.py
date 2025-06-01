import os
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
try:
    from googlesearch import search
except ImportError:
    print("No module named 'google' found. Install with: pip install google")
import re
import time
import random
import imghdr
from datetime import datetime

class Scraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'en-US,en;q=0.5'
        }
        self.request_timeout = 20
        self.search_delay = 2.5
        self.STORAGE_DIR = "storage"
        self.IMAGE_DIR = os.path.join(self.STORAGE_DIR, "images")
        self.PDF_DIR = os.path.join(self.STORAGE_DIR, "pdfs")
        os.makedirs(self.IMAGE_DIR, exist_ok=True)
        os.makedirs(self.PDF_DIR, exist_ok=True)

    def set_storage_locations(self, image_dir=None, pdf_dir=None):
        """Update storage locations and create directories"""
        if image_dir:
            self.IMAGE_DIR = image_dir
            os.makedirs(self.IMAGE_DIR, exist_ok=True)
        if pdf_dir:
            self.PDF_DIR = pdf_dir
            os.makedirs(self.PDF_DIR, exist_ok=True)
        print(f"📂 Storage locations updated:\nImages: {self.IMAGE_DIR}\nPDFs: {self.PDF_DIR}")

    def get_storage_locations(self):
        """Returns the current storage locations"""
        return {
            'images': os.path.abspath(self.IMAGE_DIR),
            'pdfs': os.path.abspath(self.PDF_DIR)
        }

    def scrape_images_and_pdfs(self, query):
        """Main method to scrape both images and PDFs"""
        print(f"\n🔍 Starting search for: '{query}'")
        
        print("\n📸 Searching for images...")
        image_urls = self._scrape_google_images(query)
        image_files = self._download_files(image_urls, "image") if image_urls else []
        
        print("\n📄 Searching for PDFs...")
        pdf_urls = self._scrape_pdfs(query)
        pdf_files = self._download_files(pdf_urls, "pdf") if pdf_urls else []
        
        return image_files, pdf_files

    def _scrape_google_images(self, query, num_images=10):
        """Scrape image URLs from Google search"""
        search_url = f"https://www.google.com/search?tbm=isch&q={query}"
        image_urls = []
        
        try:
            response = requests.get(search_url, headers=self.headers, timeout=self.request_timeout)
            soup = BeautifulSoup(response.text, "html.parser")
            
            for img in soup.find_all("img"):
                src = img.get("src") or img.get("data-src")
                if src and src.startswith(('http://', 'https://')):
                    image_urls.append(src)
                    if len(image_urls) >= num_images:
                        break
            
            return image_urls[:num_images]
            
        except Exception as e:
            print(f"❌ Image scraping failed: {e}")
            return []

    def _scrape_pdfs(self, search_text, num_results=10):
        """Scrape PDF URLs from Google search with better validation"""
        query = f"{search_text} filetype:pdf"
        pdf_urls = set()
        
        try:
            for url in search(query, num_results=num_results * 2):  # Search more to account for failures
                if len(pdf_urls) >= num_results:
                    break
                    
                # Basic URL validation
                if not url.startswith(('http://', 'https://')):
                    continue
                
                try:
                    response = requests.head(url, timeout=5, headers=self.headers)
                    content_type = response.headers.get('content-type', '').lower()
                    
                    if 'application/pdf' in content_type:
                        pdf_urls.add(url)
                        print(f"✓ Valid PDF found: {url}")
                    
                except Exception as e:
                    print(f"⚠️ Skipping URL (error checking): {url}")
                    continue
                
                time.sleep(random.uniform(1.0, 2.0))
            
            return list(pdf_urls)
            
        except Exception as e:
            print(f"❌ PDF search failed: {e}")
            return []

    def _download_files(self, urls, file_type):
        """Enhanced downloader with better PDF validation"""
        downloaded_files = []
        
        for i, url in enumerate(urls, 1):
            try:
                if not url.startswith(('http://', 'https://')):
                    print(f"⚠️ Skipping invalid URL: {url}")
                    continue

                # Determine save path
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                if file_type == "pdf":
                    filename = f"doc_{i}_{timestamp}.pdf"
                    save_dir = self.PDF_DIR
                    
                    # Additional PDF validation
                    response = requests.head(url, timeout=self.request_timeout, headers=self.headers)
                    content_type = response.headers.get('content-type', '').lower()
                    
                    if 'application/pdf' not in content_type:
                        print(f"⚠️ Skipping non-PDF content: {url}")
                        continue
                else:
                    # Image handling remains the same
                    response = requests.get(url, stream=True, timeout=self.request_timeout, headers=self.headers)
                    response.raise_for_status()
                    image_type = imghdr.what(None, h=response.content) or "jpg"
                    if image_type == "jpeg": image_type = "jpg"
                    filename = f"image_{i}_{timestamp}.{image_type}"
                    save_dir = os.path.join(self.IMAGE_DIR, image_type)
                
                os.makedirs(save_dir, exist_ok=True)
                filepath = os.path.join(save_dir, filename)
                
                # Download file with progress tracking
                response = requests.get(url, stream=True, timeout=self.request_timeout, headers=self.headers)
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                block_size = 8192
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=block_size):
                        if chunk:
                            f.write(chunk)
                
                # Verify file was saved properly
                if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                    print(f"✅ Saved {file_type}: {filename}")
                    print(f"📂 Location: {os.path.abspath(filepath)}")
                    downloaded_files.append(filepath)
                else:
                    print(f"⚠️ File may be corrupted: {filename}")
                    if os.path.exists(filepath):
                        os.remove(filepath)
                        
            except Exception as e:
                print(f"❌ Failed to download {file_type} from {url}: {e}")
                if 'filepath' in locals() and os.path.exists(filepath):
                    os.remove(filepath)
                    
        return downloaded_files

    def _is_pdf(self, url):
        """Check if URL points to a PDF and is a valid URL"""
        if not url or os.path.exists(url):  # Skip if it's a local file
            return False
        url = url.lower()
        return (url.startswith(('http://', 'https://')) and 
                (url.endswith('.pdf') or '.pdf?' in url or '.pdf#' in url))

    def _extract_pdf_links(self, url):
        """Extract PDF links from a webpage"""
        try:
            response = requests.get(url, headers=self.headers, timeout=self.request_timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            pdf_links = set()
            for link in soup.find_all('a', href=True):
                href = link['href'].strip()
                if self._is_pdf(href):
                    absolute_url = urljoin(url, href)
                    pdf_links.add(absolute_url)
            
            return list(pdf_links)
            
        except Exception as e:
            print(f"⚠️ Couldn't scan {url}: {e}")
            return []

