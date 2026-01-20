# AIReady File Converter

Convert everyday human documents (PDF, Word, Excel, PowerPoint, Images) into AI-ready formats (Markdown, JSON) with a single click.

## Features

- **Multiple Input Formats**: PDF, DOCX, XLSX, CSV, PPTX, PNG, JPG, GIF, BMP, TIFF
- **Dual Output Formats**: Markdown (.md) and JSON (.json)
- **Smart Defaults**: Spreadsheets → JSON, Documents → Markdown
- **OCR Support**: Extract text from images using Tesseract
- **Base64 Encoding**: Images encoded for AI context windows
- **Session-Based Storage**: Files auto-delete after 15 minutes
- **No Data Persistence**: Privacy-first, no permanent storage
- **Modern UI**: Clean, responsive drag-and-drop interface

## Quick Start

### Local Development

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Tesseract OCR** (for image text extraction):
   
   macOS:
   ```bash
   brew install tesseract
   ```
   
   Ubuntu/Debian:
   ```bash
   sudo apt-get install tesseract-ocr
   ```
   
   Windows:
   Download from [Tesseract GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

3. **Run the server**:
   ```bash
   python main.py
   ```
   
   Or with uvicorn directly:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Open in browser**: http://localhost:8000

### Docker Deployment

1. **Build the image**:
   ```bash
   docker build -t aiready-file-converter .
   ```

2. **Run the container**:
   ```bash
   docker run -p 8000:8000 aiready-file-converter
   ```

### Cloud Deployment

The app is ready for deployment to:

- **Render**: Connect your repo and deploy
- **Railway**: One-click deploy from GitHub
- **Fly.io**: `fly launch` and `fly deploy`
- **Any Docker host**: Use the included Dockerfile

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main web interface |
| `/api/session` | GET | Get/create session |
| `/api/upload` | POST | Upload a file |
| `/api/set-format/{file_id}` | POST | Set output format (md/json) |
| `/api/convert` | POST | Convert all uploaded files |
| `/api/download/{file_id}` | GET | Download a converted file |
| `/api/preview/{file_id}` | GET | Preview converted content |
| `/api/download-all` | GET | Download all as ZIP |
| `/api/file/{file_id}` | DELETE | Remove a file |
| `/api/clear` | DELETE | Clear all files |

## Supported Conversions

| Input | Default Output | Content Extracted |
|-------|---------------|-------------------|
| PDF | Markdown | Text, tables, page structure |
| Word (.docx) | Markdown | Headings, paragraphs, tables |
| Excel (.xlsx/.csv) | JSON | Sheets as structured records |
| PowerPoint (.pptx) | Markdown | Slides, titles, notes |
| Images | JSON | OCR text + Base64 encoding |

## Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_TOTAL_SIZE` | 10MB | Max total size for all uploads |
| `SESSION_TIMEOUT_MINUTES` | 15 | Session expiry time |

## Security

- File type validation (extension + MIME type)
- Size limits enforced
- Session isolation (UUID-based)
- Automatic cleanup of expired files
- No external API calls
- All processing done locally

## License

MIT License - Use freely for personal or commercial projects.
