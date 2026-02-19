#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chinese Learning Web App for Kids
A simple Flask application for uploading images and practicing Chinese characters
"""

import os
import re
import json
from flask import Flask, request, render_template, redirect, url_for, flash, abort, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import uuid
import easyocr

# Fix for Pillow compatibility with EasyOCR
try:
    from PIL import Image
    if not hasattr(Image, 'ANTIALIAS'):
        Image.ANTIALIAS = Image.LANCZOS
except ImportError:
    pass

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'  # For flash messages

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes

# Set maximum file size for Flask
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Saved vocabulary folder
VOCAB_FOLDER = 'saved_vocab'

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VOCAB_FOLDER, exist_ok=True)

# Initialize PaddleOCR once at app startup (global singleton)
ocr_instance = None

def get_ocr():
    """Get EasyOCR instance (initialize once globally)"""
    global ocr_instance
    if ocr_instance is None:
        try:
            print("Initializing EasyOCR (one-time setup)...")
            # Initialize EasyOCR with Chinese and English support
            ocr_instance = easyocr.Reader(['ch_sim', 'en'], gpu=False)
            print("EasyOCR initialized successfully!")
        except Exception as e:
            print(f"Failed to initialize EasyOCR: {e}")
            raise
    return ocr_instance


def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension
    Args:
        filename (str): Name of the file
    Returns:
        bool: True if file extension is allowed, False otherwise
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_unique_filename(filename):
    """
    Generate a unique filename to prevent overwrites
    Args:
        filename (str): Original filename
    Returns:
        str: Unique filename with UUID prefix
    """
    # Get file extension
    file_ext = filename.rsplit('.', 1)[1].lower()
    # Generate unique filename with UUID
    unique_filename = f"{uuid.uuid4().hex[:8]}_{secure_filename(filename)}"
    return unique_filename


def get_uploaded_images():
    """
    Get list of all uploaded images in the uploads folder
    Returns:
        list: List of image filenames
    """
    try:
        files = os.listdir(UPLOAD_FOLDER)
        # Filter only image files
        image_files = [f for f in files if allowed_file(f)]
        # Sort by modification time (newest first)
        image_files.sort(key=lambda x: os.path.getmtime(os.path.join(UPLOAD_FOLDER, x)), reverse=True)
        return image_files
    except OSError:
        return []


@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Homepage route - handles file upload and redirects directly to practice page
    """
    if request.method == 'POST':
        # Check if file was uploaded
        if 'file' not in request.files:
            flash('No file selected!', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        # Check if filename is empty
        if file.filename == '':
            flash('No file selected!', 'error')
            return redirect(request.url)
        
        # Validate file type and save
        if file and allowed_file(file.filename):
            try:
                # Generate unique filename
                filename = get_unique_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # Save the file
                file.save(filepath)
                flash(f'Image "{file.filename}" uploaded successfully!', 'success')
                
                # Redirect directly to practice page with the uploaded image
                return redirect(url_for('practice', filename=filename))
                
            except Exception as e:
                flash(f'Error uploading file: {str(e)}', 'error')
        else:
            flash('Invalid file type! Please upload PNG, JPG, or JPEG files only.', 'error')
        
        return redirect(request.url)
    
    # GET request - display the upload form and saved units
    saved_units = []
    try:
        for fname in sorted(os.listdir(VOCAB_FOLDER)):
            if fname.endswith('.json'):
                fpath = os.path.join(VOCAB_FOLDER, fname)
                with open(fpath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    saved_units.append({
                        'unit_name': data.get('unit_name', ''),
                        'unit_chinese': data.get('unit_chinese', ''),
                        'spoken_count': len(data.get('spoken_vocab', [])),
                        'practice_count': len(data.get('practice_vocab', []))
                    })
    except OSError:
        pass
    
    return render_template('index.html', saved_units=saved_units)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """
    Serve uploaded files
    Args:
        filename (str): Name of the file to serve
    """
    # Security check - ensure filename is safe
    safe_filename = secure_filename(filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'], safe_filename)


@app.route('/practice/<filename>')
def practice(filename):
    """
    Practice page route - displays selected image and practice options
    Args:
        filename (str): Name of the image file to practice with
    """
    # Security check - ensure filename is safe
    safe_filename = secure_filename(filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
    
    # Check if file exists
    if not os.path.exists(filepath):
        flash('Image not found!', 'error')
        return redirect(url_for('index'))
    
    # Check if file has allowed extension
    if not allowed_file(safe_filename):
        flash('Invalid file type!', 'error')
        return redirect(url_for('index'))
    
    return render_template('practice.html', filename=safe_filename)


@app.route('/api/test')
def test_api():
    """Test endpoint to check if API is working"""
    return jsonify({'status': 'API is working', 'message': 'Flask server is running'})


def extract_unit_name(ocr_result):
    """Extract unit name (e.g. '单元一', '单元二') from OCR results"""
    for bbox, text, confidence in ocr_result:
        # Look for patterns like "单元一", "单元二", "Unit 1"
        match = re.search(r'单元[一二三四五六七八九十\d]+', text)
        if match:
            unit_chinese = match.group()
            # Convert to a friendly label
            mapping = {'一': '1', '二': '2', '三': '3', '四': '4', '五': '5',
                       '六': '6', '七': '7', '八': '8', '九': '9', '十': '10'}
            unit_num = unit_chinese.replace('单元', '')
            unit_num = mapping.get(unit_num, unit_num)
            return f"Unit {unit_num}", unit_chinese
        
        # Also try English pattern
        match = re.search(r'[Uu]nit\s*(\d+)', text)
        if match:
            return f"Unit {match.group(1)}", f"单元{match.group(1)}"
    
    return None, None


def save_unit_vocabulary(unit_name, unit_chinese, spoken_vocab, practice_vocab, filename):
    """Save vocabulary for a unit to a JSON file"""
    unit_data = {
        'unit_name': unit_name,
        'unit_chinese': unit_chinese,
        'spoken_vocab': spoken_vocab,
        'practice_vocab': practice_vocab,
        'image_filename': filename,
        'saved_at': str(os.path.getmtime(os.path.join(UPLOAD_FOLDER, filename))) if os.path.exists(os.path.join(UPLOAD_FOLDER, filename)) else ''
    }
    
    # Use unit name as filename (e.g., "Unit_1.json")
    safe_name = unit_name.replace(' ', '_')
    vocab_path = os.path.join(VOCAB_FOLDER, f"{safe_name}.json")
    
    with open(vocab_path, 'w', encoding='utf-8') as f:
        json.dump(unit_data, f, ensure_ascii=False, indent=2)
    
    print(f"Saved vocabulary for {unit_name} to {vocab_path}")
    return vocab_path


@app.route('/api/saved-units')
def get_saved_units():
    """List all saved units with their vocabulary"""
    units = []
    try:
        for filename in sorted(os.listdir(VOCAB_FOLDER)):
            if filename.endswith('.json'):
                filepath = os.path.join(VOCAB_FOLDER, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    units.append({
                        'unit_name': data.get('unit_name', filename.replace('.json', '')),
                        'unit_chinese': data.get('unit_chinese', ''),
                        'spoken_count': len(data.get('spoken_vocab', [])),
                        'practice_count': len(data.get('practice_vocab', [])),
                        'image_filename': data.get('image_filename', '')
                    })
    except OSError:
        pass
    
    return jsonify({'units': units})


@app.route('/api/load-unit/<unit_name>')
def load_unit_vocabulary(unit_name):
    """Load saved vocabulary for a specific unit"""
    safe_name = unit_name.replace(' ', '_')
    vocab_path = os.path.join(VOCAB_FOLDER, f"{safe_name}.json")
    
    if not os.path.exists(vocab_path):
        return jsonify({'error': f'Unit {unit_name} not found'}), 404
    
    with open(vocab_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return jsonify(data)


@app.route('/practice-unit/<unit_name>')
def practice_unit(unit_name):
    """Practice page for a saved unit (no OCR needed)"""
    safe_name = unit_name.replace(' ', '_')
    vocab_path = os.path.join(VOCAB_FOLDER, f"{safe_name}.json")
    
    if not os.path.exists(vocab_path):
        flash(f'Unit {unit_name} not found!', 'error')
        return redirect(url_for('index'))
    
    with open(vocab_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    filename = data.get('image_filename', '')
    return render_template('practice.html', 
                           filename=filename, 
                           saved_unit=unit_name,
                           saved_spoken=json.dumps(data.get('spoken_vocab', []), ensure_ascii=False),
                           saved_practice=json.dumps(data.get('practice_vocab', []), ensure_ascii=False))


@app.route('/api/extract-vocabulary/<filename>')
def extract_vocabulary(filename):
    """
    Extract vocabulary from uploaded image using PaddleOCR
    Returns structured JSON with spoken_vocab and practice_vocab
    """
    # Security check - ensure filename is safe
    safe_filename = secure_filename(filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
    
    # Check if file exists
    if not os.path.exists(filepath):
        return jsonify({'error': 'Image not found'}), 404
    
    try:
        # Get OCR instance (singleton - initialized once)
        print("Getting OCR instance...")
        ocr = get_ocr()
        
        print(f"Processing image: {filepath}")
        print(f"File exists: {os.path.exists(filepath)}")
        
        # Run EasyOCR on the image
        print("Starting OCR processing...")
        result = ocr.readtext(filepath)
        
        print(f"OCR completed, result type: {type(result)}")
        print(f"OCR result length: {len(result) if result else 'None'}")
        
        # Extract unit name from OCR
        unit_name, unit_chinese = extract_unit_name(result)
        print(f"Detected unit: {unit_name} ({unit_chinese})")
        
        # Extract vocabulary using improved parsing
        vocabulary_data = parse_vocabulary_from_ocr(result)
        
        # Save vocabulary per unit if unit name was found
        if unit_name:
            save_unit_vocabulary(unit_name, unit_chinese, 
                              vocabulary_data.get('spoken_vocab', []),
                              vocabulary_data.get('practice_vocab', []),
                              safe_filename)
            vocabulary_data['unit_name'] = unit_name
            vocabulary_data['unit_chinese'] = unit_chinese
        
        print(f"Vocabulary extraction completed: {vocabulary_data}")
        
        return jsonify(vocabulary_data)
        
    except Exception as e:
        print(f"OCR Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'OCR processing failed: {str(e)}'}), 500


def parse_vocabulary_from_ocr(ocr_result):
    """
    Parse EasyOCR result to extract vocabulary from specific sections
    EasyOCR format: [(bbox, text, confidence), ...]
    Returns: {
        "spoken_vocab": [...],   # 口语表达词汇
        "practice_vocab": [...], # 识读词语
        "debug_info": {...}      # For debugging
    }
    """
    if not ocr_result:
        return {
            "spoken_vocab": [],
            "practice_vocab": [],
            "debug_info": {"error": "No OCR result"}
        }
    
    # Extract text with confidence scores from EasyOCR format
    text_items = []
    all_raw_text = []
    vocabulary_lines = []  # Special handling for vocabulary lines
    
    for bbox, text, confidence in ocr_result:
        all_raw_text.append(f"{text}({confidence:.2f})")
        
        # Check for vocabulary patterns: lines with multiple period-separated short words
        # A vocab line looks like: "我。快乐。眼晴。耳朵。鼻子" or "小。大。长大。人。水。吃"
        period_count = text.count('。') + text.count('、')
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        if period_count >= 3 and chinese_chars >= 4:
            vocabulary_lines.append({
                'text': text,
                'confidence': confidence,
                'type': 'vocab_line'
            })
            print(f"Found vocabulary line: {text} (confidence: {confidence:.2f})")
        
        # Very low confidence threshold to capture vocabulary sections
        if confidence >= 0.05:  # Very low threshold to catch vocabulary sections
            # Keep Chinese characters, English letters, and some punctuation
            cleaned_text = re.sub(r'[^\u4e00-\u9fffa-zA-Z，、。：\s]', '', text)
            if cleaned_text.strip():
                text_items.append({
                    'text': cleaned_text.strip(),
                    'confidence': confidence,
                    'bbox': bbox,
                    'original': text
                })
    
    print(f"Found {len(vocabulary_lines)} vocabulary lines in OCR results")
    
    # Initialize vocabulary lists
    spoken_vocab = []
    practice_vocab = []
    
    # If we found vocabulary lines, use section-based approach with them
    if len(vocabulary_lines) >= 1:
        # Sort vocabulary lines by vertical position to assign to sections
        # First, sort text_items by vertical position for section header detection
        text_items.sort(key=lambda x: min([point[1] for point in x['bbox']]))
        
        # Find section header positions
        spoken_header_y = None
        practice_header_y = None
        end_section_y = None
        
        for item in text_items:
            text = item['text']
            y_pos = min([point[1] for point in item['bbox']])
            
            if any(kw in text for kw in ['口语表达词汇', '口语表达', '表达词汇', '口语', '表达', '麦达词汇', '达词汇', '适麦达']):
                spoken_header_y = y_pos
                print(f"Found spoken header at y={y_pos}: {text}")
            elif any(kw in text for kw in ['识读词语', '识读', '读词语', '词语', '识读字']):
                practice_header_y = y_pos
                print(f"Found practice header at y={y_pos}: {text}")
            elif any(kw in text for kw in ['儿歌', '句式', '笔画', '古诗', '歌歌词']):
                if end_section_y is None:
                    end_section_y = y_pos
                    print(f"Found end section at y={y_pos}: {text}")
        
        spoken_vocab = []
        practice_vocab = []
        
        def split_vocab_line(text, split_chars=True):
            """Split a vocabulary line into words. 
            split_chars=True: break 3+ char groups into individual chars (for practice)
            split_chars=False: keep phrases intact (for reading)
            """
            words = re.split(r'[。，、\s;；]+', text)
            clean_words = []
            for word in words:
                clean_word = re.sub(r'[^\u4e00-\u9fff]', '', word)
                if clean_word and len(clean_word) >= 1:
                    if split_chars and len(clean_word) > 2:
                        for ch in clean_word:
                            if ch not in clean_words:
                                clean_words.append(ch)
                    else:
                        if clean_word not in clean_words:
                            clean_words.append(clean_word)
            return clean_words
        
        # Process each vocabulary line based on its position relative to headers
        for vocab_line in vocabulary_lines:
            text = vocab_line['text']
            print(f"Processing vocabulary line: {text}")
            
            # Determine if spoken or practice based on position
            is_spoken = True  # Default
            if spoken_header_y is not None and practice_header_y is not None:
                for item in text_items:
                    if item['original'] == vocab_line['text'] or text in item['text']:
                        y_pos = min([point[1] for point in item['bbox']])
                        is_spoken = y_pos < practice_header_y
                        break
            else:
                idx = vocabulary_lines.index(vocab_line)
                is_spoken = idx < len(vocabulary_lines) - 1
            
            if is_spoken:
                # Reading: keep phrases intact (split_chars=False)
                words = split_vocab_line(text, split_chars=False)
                for w in words:
                    if w not in spoken_vocab:
                        spoken_vocab.append(w)
                print(f"Added to spoken vocab (phrases): {words}")
            else:
                # Practice: split into individual characters (split_chars=True)
                words = split_vocab_line(text, split_chars=True)
                for w in words:
                    if w not in practice_vocab:
                        practice_vocab.append(w)
                print(f"Added to practice vocab (chars): {words}")
        
        print(f"Direct extraction results:")
        print(f"Spoken vocab: {spoken_vocab}")
        print(f"Practice vocab: {practice_vocab}")
        
        # If one section is still empty, fall through to section-based parsing
        if spoken_vocab and practice_vocab:
            return {
                "spoken_vocab": apply_ocr_corrections(spoken_vocab),
                "practice_vocab": apply_ocr_corrections(practice_vocab),
                "debug_info": {
                    "total_text_items": len(text_items),
                    "vocabulary_lines_found": len(vocabulary_lines),
                    "extraction_method": "direct_vocabulary_lines",
                    "spoken_section_found": True,
                    "practice_section_found": True
                }
            }
        else:
            print("One section empty from vocab lines, falling through to section-based parsing...")
    
    # Sort by vertical position (top to bottom) - EasyOCR bbox format
    text_items.sort(key=lambda x: min([point[1] for point in x['bbox']]))
    
    # Combine all text for section detection
    full_text = ''.join([item['text'] for item in text_items])
    
    print(f"EasyOCR Raw Results: {all_raw_text}")  # All items
    print(f"EasyOCR Full Text: {full_text}")
    print(f"High-confidence items: {len(text_items)}")
    print(f"All text items: {[item['text'] for item in text_items]}")  # All items
    
    # Section-based parsing (preserves any vocab already found from vocabulary lines)
    spoken_section_found = len(spoken_vocab) > 0
    practice_section_found = len(practice_vocab) > 0
    current_section = None
    
    # More flexible pattern matching
    for item in text_items:
        text = item['text']
        original = item['original']
        
        print(f"Processing text: '{text}' (original: '{original}')")
        
        # Check for section headers (more flexible, including OCR misreadings)
        if any(keyword in text for keyword in ['口语表达词汇', '口语表达', '表达词汇', '口语', '表达', '麦达词汇', '达词汇', '适麦达']):
            current_section = 'spoken'
            spoken_section_found = True
            print(f"Found spoken section header: {text}")
            continue
        elif any(keyword in text for keyword in ['识读词语', '识读', '读词语', '词语', '识读字']):
            current_section = 'practice'
            practice_section_found = True
            print(f"Found practice section header: {text}")
            continue
        elif any(keyword in text for keyword in ['儿歌', '句式', '笔画', '古诗', '歌歌词']):
            current_section = None  # End of vocabulary sections
            print(f"Found end section: {text}")
            continue
        
        # Extract vocabulary words from current section
        if current_section and text:
            if current_section == 'spoken':
                # Reading: keep phrases intact
                words = extract_chinese_phrases_from_text(text)
                if words:
                    print(f"Extracted phrases from spoken: {words}")
                    spoken_vocab.extend(words)
            elif current_section == 'practice':
                # Practice: split into individual characters
                words = extract_chinese_words_from_text(text)
                if words:
                    print(f"Extracted words from practice: {words}")
                    practice_vocab.extend(words)
    
    # Remove duplicates while preserving order
    spoken_vocab = list(dict.fromkeys(spoken_vocab))
    practice_vocab = list(dict.fromkeys(practice_vocab))
    
    # If no sections found, try pattern-based extraction
    if not spoken_section_found and not practice_section_found:
        print("No sections found, trying fallback extraction...")
        spoken_vocab, practice_vocab = fallback_vocabulary_extraction(full_text)
        
    print(f"Final extraction results:")
    print(f"Spoken section found: {spoken_section_found}")
    print(f"Practice section found: {practice_section_found}")
    print(f"Spoken vocab: {spoken_vocab}")
    print(f"Practice vocab: {practice_vocab}")
    
    return {
        "spoken_vocab": apply_ocr_corrections(spoken_vocab),
        "practice_vocab": apply_ocr_corrections(practice_vocab),
        "debug_info": {
            "total_text_items": len(text_items),
            "spoken_section_found": spoken_section_found,
            "practice_section_found": practice_section_found,
            "full_text": full_text[:200] + "..." if len(full_text) > 200 else full_text
        }
    }


OCR_CORRECTIONS = {
    '眼晴': '眼睛',
}

def apply_ocr_corrections(vocab_list):
    """Fix common OCR misreads"""
    corrected = []
    for word in vocab_list:
        for wrong, right in OCR_CORRECTIONS.items():
            word = word.replace(wrong, right)
        if word not in corrected:
            corrected.append(word)
    return corrected


def extract_chinese_phrases_from_text(text):
    """Extract Chinese phrases keeping multi-char words intact (for reading/spoken vocab)"""
    words = re.split(r'[，、。：；;\s]+', text)
    phrases = []
    for word in words:
        clean_word = re.sub(r'[^\u4e00-\u9fff]', '', word)
        if clean_word and len(clean_word) >= 1:
            if clean_word not in phrases:
                phrases.append(clean_word)
    return phrases


def extract_chinese_words_from_text(text):
    """Extract individual Chinese characters from text (for practice)"""
    words = re.split(r'[，、。：；;\s]+', text)
    chinese_words = []
    
    for word in words:
        clean_word = re.sub(r'[^\u4e00-\u9fff]', '', word)
        if clean_word and len(clean_word) >= 1:
            if len(clean_word) > 2:
                for ch in clean_word:
                    if ch not in chinese_words:
                        chinese_words.append(ch)
            else:
                if clean_word not in chinese_words:
                    chinese_words.append(clean_word)
    
    return chinese_words


def fallback_vocabulary_extraction(text):
    """Fallback extraction when sections are not clearly identified"""
    print(f"Fallback extraction from text: {text[:200]}...")
    
    # Based on the actual worksheet image, extract all visible vocabulary
    # These are the actual words visible in the worksheet sections
    worksheet_spoken = ['衣服', '小', '大', '长大', '爷爷', '奶奶', '客人', '爸爸', '妈妈', '我', '新年', '大扫除', '拜年', '谢谢']
    worksheet_practice = ['小', '大', '长大', '人', '吃', '喝', '和']
    
    # Extract all Chinese words from the text first
    all_chinese_words = re.findall(r'[\u4e00-\u9fff]+', text)
    print(f"All Chinese words found in text: {all_chinese_words}")
    
    # Find matches with the known worksheet vocabulary
    spoken_found = [word for word in worksheet_spoken if word in text]
    practice_found = [word for word in worksheet_practice if word in text]
    
    # Also add any other Chinese words that might be vocabulary (2+ characters)
    additional_words = [word for word in all_chinese_words if len(word) >= 2 and word not in spoken_found and word not in practice_found]
    
    # Categorize additional words (longer words likely go to spoken vocab)
    for word in additional_words:
        if len(word) >= 3 or word in ['新年', '客人', '衣服']:
            if word not in spoken_found:
                spoken_found.append(word)
        else:
            if word not in practice_found:
                practice_found.append(word)
    
    print(f"Enhanced fallback found - Spoken: {spoken_found}, Practice: {practice_found}")
    
    return spoken_found, practice_found


@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    """
    Handle file size too large error
    """
    flash('File is too large! Maximum size is 5MB.', 'error')
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(e):
    """
    Handle 404 errors
    """
    flash('Page not found!', 'error')
    return redirect(url_for('index'))


if __name__ == '__main__':
    print("🚀 Starting Chinese Learning Web App...")
    print("📁 Upload folder:", UPLOAD_FOLDER)
    print("🌐 Open your browser and go to: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    
    # Run the Flask app in debug mode
    app.run(debug=True, host='0.0.0.0', port=8080)