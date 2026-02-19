# 🐼 Chinese Learning Web App for Kids

A fun and interactive web application designed to help children practice Chinese characters through image uploads and engaging learning activities.

## 🌟 Features

- **📸 Image Upload**: Upload Chinese character images (PNG, JPG, JPEG)
- **🖼️ Image Gallery**: View all uploaded images as clickable thumbnails
- **🎯 Practice Mode**: Interactive practice sessions with:
  - ✍️ Stroke animation (placeholder)
  - 📖 Sentence reading (placeholder)
  - 🎵 Nursery rhyme practice (placeholder)
- **👶 Child-Friendly Design**: Colorful, large buttons, and intuitive interface
- **📱 Mobile Responsive**: Works great on tablets and phones
- **🔒 Security**: File validation, size limits, and secure filename handling

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Installation & Running

#### 🚀 Quick Start (Recommended)

**For Linux/Mac:**
```bash
# One-time setup
./setup.sh

# Run the app anytime
./run.sh
```

**For Windows:**
```batch
REM One-time setup
setup.bat

REM Run the app anytime
run.bat
```

#### 🔧 Manual Setup

1. **Navigate to the project directory:**
   ```bash
   cd /path/to/your/project
   ```

2. **Create and activate virtual environment (RECOMMENDED):**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   
   # Activate it (Linux/Mac)
   source venv/bin/activate
   
   # Activate it (Windows)
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **When done, deactivate virtual environment:**
   ```bash
   deactivate
   ```

4. **Open your browser and visit:**
   ```
   http://localhost:5000
   ```

That's it! 🎉 The app is now running and ready for your child to start learning Chinese!

## 📁 Project Structure

```
project/
│
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── .gitignore         # Git ignore file
├── setup.sh           # Linux/Mac setup script
├── setup.bat          # Windows setup script
├── run.sh             # Linux/Mac run script
├── run.bat            # Windows run script
├── venv/              # Virtual environment (created by setup)
├── uploads/           # Uploaded images storage
│   └── .gitkeep       # Keeps directory in git
├── templates/         # HTML templates
│   ├── index.html     # Homepage with upload form
│   └── practice.html  # Practice page
└── static/
    └── style.css      # Child-friendly CSS styles
```

## 🎮 How to Use

1. **Upload an Image**: 
   - Click "Choose Image File" on the homepage
   - Select a PNG, JPG, or JPEG file with Chinese characters
   - Click "Upload & Start Learning!"

2. **Practice**: 
   - Click on any uploaded image thumbnail
   - Click "Start Practice Session!" to begin learning
   - Explore the different practice modes (coming soon!)

## 📋 File Requirements

- **Supported formats**: PNG, JPG, JPEG only
- **Maximum file size**: 5MB
- **Best results**: Clear images with visible Chinese characters

## 🛡️ Security Features

- File type validation
- File size limits (5MB max)
- Secure filename handling
- Automatic filename collision prevention
- Input sanitization

## 🎨 Design Features

- **Child-friendly interface** with large, colorful buttons
- **Responsive design** that works on all devices
- **Smooth animations** and interactive elements
- **Fun color scheme** with gradients and soft colors
- **Comic Sans font** for a playful, kid-friendly look

## 🔧 Technical Details

- **Backend**: Python Flask framework
- **Frontend**: HTML5, CSS3, JavaScript
- **Templates**: Jinja2 templating engine
- **Storage**: Local file system (no database required)
- **Security**: Werkzeug secure filename utilities

## 🎨 **Hanzi Writer Integration**

The stroke animation feature now uses **Hanzi Writer**, a professional JavaScript library for Chinese character learning:

- **✅ Authentic Stroke Order**: Real Chinese character stroke sequences
- **✅ Interactive Practice**: Draw characters with real-time feedback
- **✅ Multiple Characters**: 15+ characters including numbers, family words, and basics
- **✅ Progress Tracking**: Visual feedback on practice completion
- **✅ Professional Animations**: Smooth, accurate stroke animations
- **✅ Mobile Friendly**: Touch-enabled drawing on tablets and phones

### Available Characters:
- **Basic**: 人(person), 大(big), 小(small), 水(water), 火(fire), 木(wood)
- **Numbers**: 一(one), 二(two), 三(three), 四(four), 五(five)
- **Family**: 爸(father), 妈(mother), 我(I/me), 你(you)

## 🚀 Future Enhancements

- **📖 Sentence Reading**: Audio-enabled reading comprehension
- **🎵 Nursery Rhymes**: Musical learning activities
- **🏆 Progress Tracking**: Save and track learning progress
- **🎯 More Characters**: Expand character library
- **🔊 Audio Pronunciation**: Add pinyin audio playback

## 🐛 Troubleshooting

### Common Issues:

1. **"Module not found" error**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Permission errors on uploads folder**:
   ```bash
   chmod 755 uploads/
   ```

3. **Port already in use**:
   - Change the port in `app.py`: `app.run(port=5001)`
   - Or kill the process using port 5000

4. **Images not displaying**:
   - Check that images are in the `uploads/` folder
   - Verify file permissions
   - Check browser console for errors

## 🎯 Development Notes

- The app runs in debug mode by default for development
- File uploads are stored in the local `uploads/` directory
- No database is required - all data is file-based
- The app is designed to be easily extensible for future features

## 📞 Support

If you encounter any issues:
1. Check the terminal output for error messages
2. Verify all files are in the correct locations
3. Ensure Python and pip are properly installed
4. Check file permissions for the uploads directory

---

**Happy Learning! 🎉🐼📚**

*Made with ❤️ for young Chinese language learners*

## Claude (Anthropic) Setup

If you'd like to call Anthropic Claude from this project, follow these steps:

- **Install new dependencies:**

```bash
pip install -r requirements.txt
```

- **Set your API key:** Create a `.env` file in the project root or export the environment variable `ANTHROPIC_API_KEY`.

Example `.env` file contents:

```
ANTHROPIC_API_KEY=sk-...your_api_key_here...
```

- **Run the quick test script:**

```bash
python test_claude.py
```

This project includes `claude_client.py`, a lightweight HTTP client that uses the Anthropic `complete` endpoint. It expects `ANTHROPIC_API_KEY` to be set in the environment. The test script `test_claude.py` shows a minimal example of usage.

Note: Network requests will run against Anthropic's API and consume any quota associated with your key. If you prefer to use Anthropic's official SDK instead of the simple HTTP client, install the `anthropic` package and adapt the client accordingly.

**Security Note:** If you have already posted or shared your API key (for example by pasting it into chat or committing it), rotate it immediately in the Anthropic dashboard and revoke the exposed key. Do not share API keys in public channels or version control.