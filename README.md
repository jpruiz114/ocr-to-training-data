# OCR to Training Data

Extract text from PDF files using Google Cloud Vision OCR and prepare it for training language models with nanoGPT.

## Setup

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install google-cloud-vision pdf2image pillow
```

### 3. Setup Google Cloud

1. Go to https://console.cloud.google.com/
2. Create or select a project
3. Enable Vision API: APIs & Services → Library → Search "Cloud Vision API" → Enable
4. Create service account:
   - IAM & Admin → Service Accounts → Create Service Account
   - Add role: "Cloud Vision API User"
   - Generate and download JSON key
5. Set environment variable:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=my-project-6250-1727894163971-ea4ec058ed15.json
```

Make it permanent:
```bash
echo 'export GOOGLE_APPLICATION_CREDENTIALS=my-project-6250-1727894163971-ea4ec058ed15.json' >> ~/.zshrc
```

## Usage

### Extract Text from PDFs

Single PDF:
```bash
python ocr_google_vision.py document.pdf
```

Batch process:
```bash
python ocr_google_vision.py /path/to/pdfs/ --batch
```

Options:
- `--detailed` - Use detailed document OCR (better for complex layouts)
- `--output ./custom_dir` - Specify output directory

### Consolidate OCR Results

Combine all extracted text files into one:
```bash
python combine_extracted_texts.py --auto
```

### Prepare Training Data

Convert consolidated text to nanoGPT format:
```bash
python prepare.py
```

This generates files in `prepared_training_data/`:
- `train.bin` - Training data
- `val.bin` - Validation data
- `meta.pkl` - Vocabulary metadata
- `prepare_summary.txt` - Preparation statistics

## Output Structure

### Per-PDF Results

Each processed PDF creates a directory in `ocr_google_vision_pdf/`:
- `complete_extracted_text.txt` - All pages combined
- `page_001.txt`, `page_002.txt`, etc. - Individual pages
- `extraction_summary.txt` - Statistics and API usage

### Consolidated Data

- `consolidated_extracted_text.txt` - All OCR text combined
- `consolidation_summary.txt` - Consolidation report

## Project Structure

```
ocr-to-training-data/
├── ocr_google_vision.py              # Google Cloud Vision OCR script
├── combine_extracted_texts.py        # Consolidation script
├── prepare.py                        # Training data preparation
├── pdf/                              # Source PDF files (symlinked)
├── ocr_google_vision_pdf/            # OCR output directory
│   ├── [document-name]/             # Per-document results
│   ├── consolidated_extracted_text.txt
│   ├── consolidation_summary.txt
│   └── notes.txt                    # Processing commands
└── prepared_training_data/          # Binary training data
    ├── train.bin
    ├── val.bin
    ├── meta.pkl
    └── prepare_summary.txt
```

## Deactivate Virtual Environment

```bash
deactivate
```
