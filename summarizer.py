import torch
from transformers import pipeline, logging
from PyPDF2 import PdfReader
import warnings

# Suppress unnecessary  warnings
warnings.filterwarnings("ignore")
logging.set_verbosity_error()

def load_summarizer():
    """Loads the best available summarization model with fallback"""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"✅ Device set to use: {device}")


    try:
        return pipeline(
            "summarization",
            model="facebook/bart-large-cnn",
            device=0 if device == "cuda" else -1,
            truncation=True
        )
    except Exception as e:
        print(f"❌ Failed to load BART model: {e}\n🔁 Using T5-small as fallback")
        return pipeline(
            "summarization",
            model="t5-small",
            device=0 if device == "cuda" else -1,
            truncation=True
        )

summarizer = load_summarizer()

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file with improved error handling"""
    try:
        reader = PdfReader(pdf_path)
        text = []
        
        # Check if PDF is encrypted
        if reader.is_encrypted:
            try:
                reader.decrypt('')  # Try empty password
            except:
                return "⚠️ Cannot process encrypted PDF"
        
        for page in reader.pages:
            try:
                page_text = page.extract_text()
                if page_text and len(page_text.strip()) > 50:  # Only add meaningful content
                    text.append(page_text.strip())
            except Exception as page_error:
                print(f"⚠️ Page extraction error: {page_error}")
                continue
                
        full_text = "\n".join(text)
        if not full_text.strip():
            return "⚠️ No readable text content found in PDF"
        return full_text
        
    except Exception as e:
        print(f"❌ PDF read error: {e}")
        return f"⚠️ Failed to read PDF: {str(e)}"

def split_text(text, max_chunk_size=500):
    """Split text into smaller chunks for better summarization"""
    if len(text) <= max_chunk_size:
        return [text]
        
    chunks = []
    sentences = text.replace('\n', ' ').split('.')
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence = sentence.strip() + '.'
        sentence_length = len(sentence)
        
        if current_length + sentence_length <= max_chunk_size:
            current_chunk.append(sentence)
            current_length += sentence_length
        else:
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            current_chunk = [sentence]
            current_length = sentence_length
            
    if current_chunk:
        chunks.append(' '.join(current_chunk))
        
    return chunks

def summarize_text(text, max_length=150):
    """Generates summary with improved error handling"""
    if not text or "⚠️" in text:
        return text  # Return original warning

    try:
        return summarizer(
            text,
            max_length=max_length,
            min_length=50,
            do_sample=False,
            truncation=True
        )[0]['summary_text']
    except Exception as e:
        print(f"❌ Summarization error: {e}")
        return "⚠️ Summary generation failed"

def process_document(pdf_path, progress_callback=None):
    """Enhanced processing pipeline with better error handling"""
    if progress_callback:
        progress_callback("Extracting text...")
    
    text = extract_text_from_pdf(pdf_path)
    if text.startswith("⚠️"):
        return text
    
    try:
        if progress_callback:
            progress_callback("Generating summary...")
        
        # Split into manageable chunks
        chunks = split_text(text)
        if len(chunks) == 0:
            return "⚠️ No valid text to summarize"
            
        summaries = []
        for i, chunk in enumerate(chunks, 1):
            if progress_callback:
                progress_callback(f"Processing section {i}/{len(chunks)}")
                
            summary = summarize_text(chunk, max_length=150 if len(chunks) > 1 else 250)
            if summary and not summary.startswith("⚠️"):
                summaries.append(summary)
        
        if not summaries:
            return "⚠️ Could not generate meaningful summary"
            
        # Combine summaries intelligently
        final_summary = " ".join(summaries)
        if len(summaries) > 1:
            # Create a meta-summary if we have multiple chunks
            final_summary = summarize_text(final_summary, max_length=250)
            
        return final_summary
        
    except Exception as e:
        print(f"❌ Processing error: {e}")
        return f"⚠️ Summary generation failed: {str(e)}"

import os

def summarize_pdfs(folder_path):
    """Summarizes all PDFs in a given folder and prints them."""
    if not os.path.exists(folder_path):
        print(f"❌ Folder not found: {folder_path}")
        return {}

    summaries = {}
    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")]

    if not pdf_files:
        print("⚠️ No PDFs found in the folder.")
        return {}

    print(f"🔍 Found {len(pdf_files)} PDFs to summarize...\n")

    for i, pdf_name in enumerate(pdf_files, 1):
        pdf_path = os.path.join(folder_path, pdf_name)
        print(f"📄 [{i}/{len(pdf_files)}] Summarizing: {pdf_name}")
        summary = process_document(pdf_path)
        summaries[pdf_name] = summary
        print(f"📝 Summary for {pdf_name}:\n{summary}\n{'-'*60}")

    return summaries


if __name__ == "__main__":
    pdf_folder = r"C:\Users\Administrator\Desktop\Content Grabber\storage\google\pdfs"
    summarize_pdfs(pdf_folder)
