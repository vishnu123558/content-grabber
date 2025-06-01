import requests
from bs4 import BeautifulSoup
from googlesearch import search
import re
from urllib.parse import urljoin  # Added missing import

def google_search(query, num_results=5):
    """Searches Google and returns the top URLs."""
    return list(search(query, num_results=num_results))

def extract_images_and_pdfs(url):
    """Improved PDF detection with regex"""
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract image URLs with absolute paths
        images = []
        for img in soup.find_all("img", src=True):
            img_url = img["src"]
            if not img_url.startswith(("http", "https")):
                img_url = urljoin(url, img_url)
            images.append(img_url)
        
        # Extract PDF URLs with better pattern matching
        pdf_pattern = re.compile(r"\.pdf($|\?|#)", re.IGNORECASE)
        pdfs = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if pdf_pattern.search(href):
                if not href.startswith(("http", "https")):
                    href = urljoin(url, href)
                pdfs.append(href)
        
        return images, pdfs

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch {url}: {e}")
        return [], []
    except Exception as e:
        print(f"❌ Unexpected error processing {url}: {e}")
        return [], []

def scrape_images_and_pdfs(query):
    """Searches Google and scrapes images & PDFs from the top results."""
    search_results = google_search(query)
    
    all_images = []
    all_pdfs = []

    for url in search_results:
        print(f"🔍 Scraping: {url}")
        images, pdfs = extract_images_and_pdfs(url)
        all_images.extend(images)
        all_pdfs.extend(pdfs)

    return all_images, all_pdfs

if __name__ == "__main__":
    query = input("🔍 Enter keyword or sentence: ")
    images, pdfs = scrape_images_and_pdfs(query)

    print("\n📸 Found Images:")
    for img in images:
        print(img)

    print("\n📄 Found PDFs:")
    for pdf in pdfs:
        print(pdf)

import requests
from bs4 import BeautifulSoup
from googlesearch import search
import re
from urllib.parse import urljoin

def google_search(query, num_results=5):
    """Searches Google and returns the top URLs."""
    return list(search(query, num_results=num_results))

def extract_images_and_pdfs(url):
    """Extracts both images and PDFs from a webpage with proper URL handling"""
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract images (including relative paths)
        images = []
        for img in soup.find_all("img", src=True):
            img_url = img["src"]
            if not img_url.startswith(("http", "https")):
                img_url = urljoin(url, img_url)
            images.append(img_url)
        
        # Extract PDFs with better pattern matching
        pdf_pattern = re.compile(r"\.pdf($|\?|#)", re.IGNORECASE)
        pdfs = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if pdf_pattern.search(href):
                if not href.startswith(("http", "https")):
                    href = urljoin(url, href)
                pdfs.append(href)
        
        return images, pdfs

    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        return [], []

def scrape_images_and_pdfs(query):
    """Searches Google and scrapes both images & PDFs from top results"""
    search_results = google_search(query)
    
    all_images = []
    all_pdfs = []

    for url in search_results:
        print(f"🔍 Scraping: {url}")
        images, pdfs = extract_images_and_pdfs(url)
        all_images.extend(images)
        all_pdfs.extend(pdfs)
        print(f"Found {len(images)} images and {len(pdfs)} PDFs")

    return all_images, all_pdfs