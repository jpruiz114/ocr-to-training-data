#!/usr/bin/env python3
"""
Google Cloud Vision OCR for PDF files
High-quality OCR using Google's Vision API

Requirements:
- pip install google-cloud-vision pdf2image pillow
- Google Cloud account with Vision API enabled
- Service account JSON key or gcloud authentication

Cost: 1,000 free requests per month, then $1.50 per 1,000 requests
"""

import os
import io
from google.cloud import vision
from pdf2image import convert_from_path
from PIL import Image
import argparse
import time
from pathlib import Path

class GoogleVisionOCR:
    def __init__(self):
        self.client = None
        self.setup_client()
    
    def setup_client(self):
        """Initialize Google Cloud Vision client with error handling"""
        try:
            self.client = vision.ImageAnnotatorClient()
            print("✅ Google Vision API client initialized successfully")
        except Exception as e:
            print(f"❌ Error setting up Vision API client: {e}")
            print("\n💡 Authentication Help:")
            print("Option 1 - Service Account JSON:")
            print("  export GOOGLE_APPLICATION_CREDENTIALS='path/to/service-account.json'")
            print("\nOption 2 - Application Default Credentials:")
            print("  gcloud auth application-default login")
            print("\nOption 3 - Check your Google Cloud project:")
            print("  gcloud config get-value project")
            self.client = None
    
    def test_connection(self):
        """Test if the Vision API is working"""
        if not self.client:
            return False
        
        try:
            # Create a minimal test image
            test_image = Image.new('RGB', (100, 50), color='white')
            img_byte_arr = io.BytesIO()
            test_image.save(img_byte_arr, format='PNG')
            
            # Test the API
            image = vision.Image(content=img_byte_arr.getvalue())
            response = self.client.text_detection(image=image)
            
            if response.error.message:
                print(f"❌ Vision API error: {response.error.message}")
                return False
            
            print("✅ Vision API connection test successful")
            return True
            
        except Exception as e:
            print(f"❌ Vision API test failed: {e}")
            return False
    
    def convert_pdf_to_images(self, pdf_path, dpi=300):
        """Convert PDF pages to PIL Images"""
        try:
            print(f"📄 Converting PDF to images (DPI: {dpi})...")
            pages = convert_from_path(pdf_path, dpi=dpi, fmt='PNG')
            print(f"✅ Converted {len(pages)} pages")
            return pages
        except Exception as e:
            print(f"❌ Error converting PDF: {e}")
            print("💡 Make sure you have poppler installed:")
            print("   macOS: brew install poppler")
            print("   Ubuntu: sudo apt-get install poppler-utils")
            return []
    
    def image_to_bytes(self, pil_image, format='PNG', quality=95):
        """Convert PIL Image to bytes for Vision API"""
        img_byte_arr = io.BytesIO()
        if format.upper() == 'JPEG':
            pil_image.save(img_byte_arr, format='JPEG', quality=quality, optimize=True)
        else:
            pil_image.save(img_byte_arr, format='PNG', optimize=True)
        return img_byte_arr.getvalue()
    
    def extract_text_from_image(self, image_bytes):
        """Extract text from image using Google Vision API"""
        if not self.client:
            return "ERROR: Vision API client not initialized"
        
        try:
            # Create Vision API image object
            image = vision.Image(content=image_bytes)
            
            # Add language hints to restrict to English/Latin script
            image_context = vision.ImageContext(language_hints=['en'])
            
            # Perform text detection
            response = self.client.text_detection(image=image, image_context=image_context)
            
            # Check for API errors
            if response.error.message:
                return f"API Error: {response.error.message}"
            
            # Extract text
            if response.text_annotations:
                # The first annotation contains all detected text
                full_text = response.text_annotations[0].description
                return full_text if full_text else "No text detected"
            else:
                return "No text found in image"
                
        except Exception as e:
            return f"Error processing image: {str(e)}"
    
    def get_detailed_text_info(self, image_bytes):
        """Get detailed text information including bounding boxes and confidence"""
        if not self.client:
            return None
        
        try:
            image = vision.Image(content=image_bytes)
            
            # Add language hints to restrict to English/Latin script
            image_context = vision.ImageContext(language_hints=['en'])
            
            response = self.client.document_text_detection(image=image, image_context=image_context)
            
            if response.error.message:
                print(f"API Error: {response.error.message}")
                return None
            
            document = response.full_text_annotation
            if not document:
                return None
            
            # Extract detailed information
            text_info = {
                'text': document.text,
                'confidence': 0,
                'word_count': 0,
                'blocks': []
            }
            
            # Calculate average confidence and word count
            total_confidence = 0
            word_count = 0
            
            for page in document.pages:
                for block in page.blocks:
                    block_text = ""
                    block_confidence = 0
                    block_words = 0
                    
                    for paragraph in block.paragraphs:
                        for word in paragraph.words:
                            word_text = ''.join([symbol.text for symbol in word.symbols])
                            block_text += word_text + " "
                            block_confidence += word.confidence
                            block_words += 1
                            word_count += 1
                            total_confidence += word.confidence
                    
                    if block_words > 0:
                        text_info['blocks'].append({
                            'text': block_text.strip(),
                            'confidence': block_confidence / block_words,
                            'word_count': block_words
                        })
            
            if word_count > 0:
                text_info['confidence'] = total_confidence / word_count
                text_info['word_count'] = word_count
            
            return text_info
            
        except Exception as e:
            print(f"Error getting detailed text info: {e}")
            return None
    
    def process_pdf(self, pdf_path, output_dir="google_vision_extracted", detailed=False, dpi=300):
        """
        Main function to process PDF and extract text using Google Vision API
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save results
            detailed: If True, uses document_text_detection for better quality
            dpi: DPI for PDF to image conversion
        """
        if not self.client:
            print("❌ Cannot process PDF: Vision API client not initialized")
            return False
        
        print(f"🔍 Processing PDF: {pdf_path}")
        print(f"📁 Output directory: {output_dir}")
        print(f"📊 Mode: {'Detailed Document OCR' if detailed else 'Standard Text Detection'}")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Convert PDF to images
        pages = self.convert_pdf_to_images(pdf_path, dpi)
        if not pages:
            return False
        
        # Process each page
        all_text = []
        total_words = 0
        total_confidence = 0
        api_calls = 0
        
        for i, page in enumerate(pages, 1):
            print(f"\n🔄 Processing page {i}/{len(pages)}...")
            start_time = time.time()
            
            # Convert to bytes (use JPEG for smaller size, faster upload)
            image_bytes = self.image_to_bytes(page, format='JPEG', quality=85)
            
            if detailed:
                # Use detailed document text detection
                text_info = self.get_detailed_text_info(image_bytes)
                if text_info:
                    text = text_info['text']
                    confidence = text_info['confidence']
                    word_count = text_info['word_count']
                else:
                    text = "Error processing page"
                    confidence = 0
                    word_count = 0
            else:
                # Use standard text detection
                text = self.extract_text_from_image(image_bytes)
                confidence = 0  # Standard detection doesn't provide confidence
                word_count = len(text.split()) if text else 0
            
            api_calls += 1
            
            # Format page text
            page_header = f"{'='*60}\nPAGE {i}\n{'='*60}\n"
            page_text = page_header + (text or "No text detected") + "\n\n"
            all_text.append(page_text)
            
            # Update totals
            total_words += word_count
            if confidence > 0:
                total_confidence += confidence
            
            # Save individual page
            page_file = os.path.join(output_dir, f"page_{i:03d}.txt")
            with open(page_file, "w", encoding="utf-8") as f:
                f.write(text or "No text detected")
            
            # Progress info
            elapsed = time.time() - start_time
            confidence_str = f", confidence: {confidence:.1f}%" if confidence > 0 else ""
            print(f"✅ Page {i}: {len(text or '')} chars, {word_count} words{confidence_str}")
            print(f"   Processing time: {elapsed:.1f}s")
        
        # Save combined results
        combined_text = "".join(all_text)
        combined_file = os.path.join(output_dir, "complete_extracted_text.txt")
        
        with open(combined_file, "w", encoding="utf-8") as f:
            f.write(combined_text)
        
        # Create summary report
        avg_confidence = total_confidence / len(pages) if total_confidence > 0 else 0
        total_chars = len(combined_text)
        
        summary = f"""
Google Cloud Vision OCR Summary
===============================
PDF File: {pdf_path}
Processing Date: {time.strftime('%Y-%m-%d %H:%M:%S')}

Statistics:
- Pages processed: {len(pages)}
- Total characters: {total_chars:,}
- Total words: {total_words:,}
- API calls made: {api_calls}

Cost Information:
- API calls used: {api_calls}
- Estimated cost: ${api_calls * 0.0015:.4f} (after free tier)

Files Generated:
- Combined text: complete_extracted_text.txt
- Individual pages: page_001.txt to page_{len(pages):03d}.txt
- This summary: extraction_summary.txt
        """
        
        summary_file = os.path.join(output_dir, "extraction_summary.txt")
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary.strip())
        
        # Print summary
        print(f"\n🎉 EXTRACTION COMPLETE!")
        print(f"📊 Statistics:")
        print(f"   • Pages processed: {len(pages)}")
        print(f"   • Total characters: {total_chars:,}")
        print(f"   • Total words: {total_words:,}")
        print(f"   • API calls used: {api_calls}")
        print(f"💰 Cost: ${api_calls * 0.0015:.4f} (after free 1,000/month)")
        print(f"📁 Output files: {output_dir}/")
        
        return True

def process_multiple_pdfs(pdf_directory, output_base_dir="batch_google_vision", detailed=False):
    """Process multiple PDFs using Google Vision API"""
    pdf_files = list(Path(pdf_directory).glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ No PDF files found in {pdf_directory}")
        return
    
    print(f"📚 Found {len(pdf_files)} PDF files")
    
    # Initialize OCR processor
    ocr = GoogleVisionOCR()
    if not ocr.test_connection():
        print("❌ Cannot proceed without working Vision API connection")
        return
    
    total_api_calls = 0
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n{'='*70}")
        print(f"📖 Processing {i}/{len(pdf_files)}: {pdf_file.name}")
        print(f"{'='*70}")
        
        # Create output directory for this PDF
        safe_name = pdf_file.stem.replace(" ", "_")
        output_dir = os.path.join(output_base_dir, safe_name)
        
        try:
            success = ocr.process_pdf(str(pdf_file), output_dir, detailed)
            if success:
                print(f"✅ {pdf_file.name}: SUCCESS")
            else:
                print(f"❌ {pdf_file.name}: FAILED")
        except Exception as e:
            print(f"❌ {pdf_file.name}: ERROR - {e}")
    
    print(f"\n💰 Estimated total cost: ${total_api_calls * 0.0015:.4f}")

def main():
    parser = argparse.ArgumentParser(description="Extract text from PDFs using Google Cloud Vision API")
    parser.add_argument("pdf_path", nargs="?", help="Path to PDF file or directory")
    parser.add_argument("--output", "-o", default="google_vision_extracted", help="Output directory")
    parser.add_argument("--detailed", action="store_true", help="Use detailed document OCR (better quality)")
    parser.add_argument("--dpi", type=int, default=300, help="DPI for image conversion (default: 300)")
    parser.add_argument("--batch", action="store_true", help="Process all PDFs in directory")
    parser.add_argument("--test", action="store_true", help="Test Vision API connection only")
    
    args = parser.parse_args()
    
    if args.test:
        ocr = GoogleVisionOCR()
        if ocr.test_connection():
            print("🎉 Google Vision API is ready to use!")
        else:
            print("❌ Google Vision API setup needs attention")
    elif args.pdf_path:
        if args.batch:
            process_multiple_pdfs(args.pdf_path, args.output, args.detailed)
        else:
            if os.path.exists(args.pdf_path):
                ocr = GoogleVisionOCR()
                if ocr.test_connection():
                    ocr.process_pdf(args.pdf_path, args.output, args.detailed, args.dpi)
                else:
                    print("❌ Cannot proceed without working Vision API connection")
            else:
                print(f"❌ File not found: {args.pdf_path}")
    else:
        print("Google Cloud Vision OCR Tool")
        print("\nUsage:")
        print("  python ocr_google_vision.py document.pdf")
        print("  python ocr_google_vision.py document.pdf --detailed")
        print("  python ocr_google_vision.py /path/to/pdfs/ --batch")
        print("  python ocr_google_vision.py --test")
        print("\nOptions:")
        print("  --output DIR     Output directory")
        print("  --detailed       Use document OCR (better quality)")
        print("  --dpi N          Image resolution (default: 300)")
        print("  --batch          Process all PDFs in directory")
        print("  --test           Test API connection")
        print("\nSetup:")
        print("  1. pip install google-cloud-vision pdf2image")
        print("  2. Set GOOGLE_APPLICATION_CREDENTIALS or run 'gcloud auth application-default login'")
        print("  3. Enable Vision API in Google Cloud Console")

if __name__ == "__main__":
    main()
