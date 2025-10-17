#!/usr/bin/env python3
"""
Combine all complete_extracted_text.txt files from subdirectories
into one consolidated file at the script level.

This script will:
1. Find all complete_extracted_text.txt files in subdirectories
2. Sort them by directory name (alphabetical order)
3. Combine them with clear separators
4. Save as consolidated_extracted_text.txt
"""

import os
from pathlib import Path
import datetime

def find_extracted_text_files(base_dir="ocr_google_vision_pdf"):
    """Find all complete_extracted_text.txt files in subdirectories"""
    base_path = Path(base_dir)
    text_files = []
    
    # Look for complete_extracted_text.txt files in subdirectories
    for item in base_path.iterdir():
        if item.is_dir():
            text_file = item / "complete_extracted_text.txt"
            if text_file.exists():
                text_files.append((item.name, text_file))
    
    # Sort by directory name for consistent ordering
    text_files.sort(key=lambda x: x[0])
    
    return text_files

def combine_text_files(text_files, output_file="consolidated_extracted_text.txt"):
    """Combine all text files into one consolidated file"""
    
    if not text_files:
        print("❌ No complete_extracted_text.txt files found in subdirectories")
        return False
    
    print(f"📚 Found {len(text_files)} extracted text files to combine:")
    for dir_name, file_path in text_files:
        file_size = file_path.stat().st_size
        print(f"   • {dir_name} ({file_size:,} bytes)")
    
    # Create consolidated file
    total_chars = 0
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Write header
        header = f"""
{'='*80}
CONSOLIDATED EXTRACTED TEXT
{'='*80}
Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Source: Google Cloud Vision OCR
Total documents: {len(text_files)}
{'='*80}

"""
        outfile.write(header)
        
        # Process each file
        for i, (dir_name, file_path) in enumerate(text_files, 1):
            try:
                print(f"🔄 Processing {i}/{len(text_files)}: {dir_name}")
                
                # Read the source file
                with open(file_path, 'r', encoding='utf-8') as infile:
                    content = infile.read().strip()
                
                if not content:
                    content = "[No text content found]"
                
                # Write document separator and content
                separator = f"""
{'='*80}
DOCUMENT {i}: {dir_name}
{'='*80}
Source File: {file_path}
Characters: {len(content):,}
{'='*80}

"""
                outfile.write(separator)
                outfile.write(content)
                outfile.write("\n\n")
                
                total_chars += len(content)
                
            except Exception as e:
                error_msg = f"❌ Error processing {dir_name}: {e}\n\n"
                outfile.write(error_msg)
                print(f"❌ Error processing {dir_name}: {e}")
        
        # Write footer
        footer = f"""
{'='*80}
CONSOLIDATION COMPLETE
{'='*80}
Total documents processed: {len(text_files)}
Total characters: {total_chars:,}
Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*80}
"""
        outfile.write(footer)
    
    return True, total_chars

def generate_summary_report(text_files, output_file, total_chars):
    """Generate a summary report of the consolidation"""
    
    summary_file = "ocr_google_vision_pdf/consolidation_summary.txt"
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("CONSOLIDATION SUMMARY REPORT\n")
        f.write("="*50 + "\n\n")
        f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Output file: {output_file}\n")
        f.write(f"Total documents: {len(text_files)}\n")
        f.write(f"Total characters: {total_chars:,}\n\n")
        
        f.write("PROCESSED DOCUMENTS:\n")
        f.write("-" * 30 + "\n")
        
        for i, (dir_name, file_path) in enumerate(text_files, 1):
            try:
                file_size = file_path.stat().st_size
                # Get character count
                with open(file_path, 'r', encoding='utf-8') as infile:
                    char_count = len(infile.read())
                
                f.write(f"{i:2d}. {dir_name}\n")
                f.write(f"    File: {file_path}\n")
                f.write(f"    Size: {file_size:,} bytes\n")
                f.write(f"    Characters: {char_count:,}\n\n")
                
            except Exception as e:
                f.write(f"{i:2d}. {dir_name} - ERROR: {e}\n\n")
    
    print(f"📊 Summary report saved: {summary_file}")

def main():
    """Main function"""
    import sys
    
    print("🔍 Combining extracted text files from OCR results...")
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Find all text files
    text_files = find_extracted_text_files()
    
    if not text_files:
        print("\n💡 No complete_extracted_text.txt files found.")
        print("Make sure you have run Google Vision OCR on some PDFs first.")
        return
    
    # Confirm before proceeding
    print(f"\n📋 Ready to combine {len(text_files)} files:")
    for dir_name, _ in text_files:
        print(f"   • {dir_name}")
    
    # Check for --auto flag to skip confirmation
    if '--auto' in sys.argv:
        print("\n🔄 Auto mode: proceeding without confirmation...")
        response = 'y'
    else:
        try:
            response = input(f"\nContinue? (y/N): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n❌ Operation cancelled.")
            return
        
    if response != 'y':
        print("❌ Operation cancelled.")
        return
    
    # Combine files
    output_file = "ocr_google_vision_pdf/consolidated_extracted_text.txt"
    print(f"\n🔄 Combining files into: {output_file}")
    
    success, total_chars = combine_text_files(text_files, output_file)
    
    if success:
        # Generate summary report
        generate_summary_report(text_files, output_file, total_chars)
        
        # Final summary
        output_size = Path(output_file).stat().st_size
        print(f"\n🎉 CONSOLIDATION COMPLETE!")
        print(f"📄 Output file: {output_file}")
        print(f"📊 File size: {output_size:,} bytes")
        print(f"📊 Total characters: {total_chars:,}")
        print(f"📚 Documents combined: {len(text_files)}")
        print(f"📋 Summary report: ocr_google_vision_pdf/consolidation_summary.txt")
        
        # Show first few lines as preview
        print(f"\n👀 Preview (first 300 characters):")
        print("-" * 50)
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                preview = f.read(300)
                print(preview)
                if len(preview) >= 300:
                    print("...")
        except Exception as e:
            print(f"Error reading preview: {e}")
        
    else:
        print("❌ Consolidation failed.")

if __name__ == "__main__":
    main()
