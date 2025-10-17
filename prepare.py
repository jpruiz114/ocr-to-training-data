"""
Prepare the OCR extracted text dataset for character-level language modeling.
Takes the consolidated_extracted_text.txt file from Google Vision OCR results
and prepares it for training by encoding characters to integers.
Will save train.bin, val.bin containing the ids, and meta.pkl containing the
encoder and decoder and some other related info.
"""
import os
import pickle
import numpy as np

# use the consolidated extracted text from OCR results
input_file_path = 'ocr_google_vision_pdf/consolidated_extracted_text.txt'

# output directory for prepared training data
data_dir = 'prepared_training_data'
os.makedirs(data_dir, exist_ok=True)

if not os.path.exists(input_file_path):
    print(f"❌ Error: {input_file_path} not found!")
    print("💡 Please run the OCR processing first and then combine_extracted_texts.py")
    print("   to generate the consolidated_extracted_text.txt file")
    exit(1)

print(f"📄 Reading OCR text from: {input_file_path}")
with open(input_file_path, 'r', encoding='utf-8') as f:
    data = f.read()

print(f"📊 Length of dataset in characters: {len(data):,}")

# get all the unique characters that occur in this text
chars = sorted(list(set(data)))
vocab_size = len(chars)
print(f"🔤 All unique characters ({vocab_size}):")
print(''.join(chars))
print(f"📚 Vocab size: {vocab_size:,}")

# create a mapping from characters to integers
stoi = { ch:i for i,ch in enumerate(chars) }
itos = { i:ch for i,ch in enumerate(chars) }

def encode(s):
    """Encoder: take a string, output a list of integers"""
    return [stoi[c] for c in s]

def decode(l):
    """Decoder: take a list of integers, output a string"""
    return ''.join([itos[i] for i in l])

# create the train and test splits (90% train, 10% validation)
n = len(data)
train_data = data[:int(n*0.9)]
val_data = data[int(n*0.9):]

print(f"✂️  Splitting data:")
print(f"   Training: {len(train_data):,} characters ({len(train_data)/n*100:.1f}%)")
print(f"   Validation: {len(val_data):,} characters ({len(val_data)/n*100:.1f}%)")

# encode both to integers
print("🔄 Encoding text to integers...")
train_ids = encode(train_data)
val_ids = encode(val_data)
print(f"✅ Train has {len(train_ids):,} tokens")
print(f"✅ Val has {len(val_ids):,} tokens")

# use uint16 dtype to match nanoGPT's train.py expectations
# (train.py hardcodes np.uint16 when reading data files)
dtype = np.uint16
print(f"💾 Using uint16 dtype (required by nanoGPT train.py, vocab_size={vocab_size})")

# export to bin files
train_ids = np.array(train_ids, dtype=dtype)
val_ids = np.array(val_ids, dtype=dtype)

train_file = os.path.join(data_dir, 'train.bin')
val_file = os.path.join(data_dir, 'val.bin')

print(f"💾 Saving training data to: {train_file}")
train_ids.tofile(train_file)
print(f"💾 Saving validation data to: {val_file}")
val_ids.tofile(val_file)

# save the meta information as well, to help us encode/decode later
meta = {
    'vocab_size': vocab_size,
    'itos': itos,
    'stoi': stoi,
    'data_source': 'Google Cloud Vision OCR - consolidated_extracted_text.txt',
    'total_chars': len(data),
    'train_chars': len(train_data),
    'val_chars': len(val_data),
    'dtype': str(dtype)
}

meta_file = os.path.join(data_dir, 'meta.pkl')
print(f"💾 Saving metadata to: {meta_file}")
with open(meta_file, 'wb') as f:
    pickle.dump(meta, f)

# create a summary report
summary_file = os.path.join(data_dir, 'prepare_summary.txt')
print(f"📋 Creating summary report: {summary_file}")

with open(summary_file, 'w', encoding='utf-8') as f:
    f.write("OCR TEXT PREPARATION SUMMARY\n")
    f.write("="*50 + "\n\n")
    f.write(f"Source file: consolidated_extracted_text.txt\n")
    f.write(f"Data source: Google Cloud Vision OCR\n")
    f.write(f"Total characters: {len(data):,}\n")
    f.write(f"Unique characters (vocab): {vocab_size:,}\n")
    f.write(f"Data type: {dtype}\n\n")
    
    f.write("TRAIN/VAL SPLIT:\n")
    f.write("-" * 20 + "\n")
    f.write(f"Training data: {len(train_data):,} chars ({len(train_data)/n*100:.1f}%)\n")
    f.write(f"Validation data: {len(val_data):,} chars ({len(val_data)/n*100:.1f}%)\n")
    f.write(f"Training tokens: {len(train_ids):,}\n")
    f.write(f"Validation tokens: {len(val_ids):,}\n\n")
    
    f.write("OUTPUT FILES:\n")
    f.write("-" * 15 + "\n")
    f.write(f"• train.bin - Training data ({len(train_ids):,} tokens)\n")
    f.write(f"• val.bin - Validation data ({len(val_ids):,} tokens)\n")
    f.write(f"• meta.pkl - Vocabulary and metadata\n")
    f.write(f"• prepare_summary.txt - This summary\n\n")
    
    f.write("VOCABULARY PREVIEW:\n")
    f.write("-" * 20 + "\n")
    f.write(f"Characters: {''.join(chars)}\n\n")
    
    f.write("SAMPLE ENCODING TEST:\n")
    f.write("-" * 22 + "\n")
    test_text = data[:100].strip()
    test_encoded = encode(test_text)
    test_decoded = decode(test_encoded)
    f.write(f"Original:  {repr(test_text)}\n")
    f.write(f"Encoded:   {test_encoded[:20]}... (showing first 20 tokens)\n")
    f.write(f"Decoded:   {repr(test_decoded)}\n")
    f.write(f"Match:     {test_text == test_decoded}\n")

print(f"\n🎉 PREPARATION COMPLETE!")
print(f"📊 Dataset Statistics:")
print(f"   • Total characters: {len(data):,}")
print(f"   • Vocabulary size: {vocab_size:,}")
print(f"   • Training tokens: {len(train_ids):,}")
print(f"   • Validation tokens: {len(val_ids):,}")
print(f"   • Data type: {dtype}")
print(f"\n📁 Output Files Created in {data_dir}/:")
print(f"   • train.bin ({os.path.getsize(train_file):,} bytes)")
print(f"   • val.bin ({os.path.getsize(val_file):,} bytes)")  
print(f"   • meta.pkl")
print(f"   • prepare_summary.txt")
print(f"\n🚀 Ready for training with nanoGPT!")
print(f"💡 You can now train a model on this OCR text data using:")
print(f"   python train.py config/train_ocr_vision_char.py")
