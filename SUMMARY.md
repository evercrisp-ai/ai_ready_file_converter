# Human → AI Format Converter: Summary

## What It Is

A web-based tool that converts everyday human documents into formats optimized for AI processing. It bridges the gap between human-readable files and AI-consumable data.

## What It Does

The converter takes common file formats that humans use daily and transforms them into structured formats (Markdown and JSON) that AI systems can easily parse and understand.

### Input Formats
- **Documents**: PDF, Word (.docx)
- **Spreadsheets**: Excel (.xlsx), CSV
- **Presentations**: PowerPoint (.pptx)
- **Images**: PNG, JPG, GIF, BMP, TIFF

### Output Formats
- **Markdown (.md)**: Human-readable structured text, ideal for documents and presentations
- **JSON (.json)**: Machine-parseable structured data, ideal for spreadsheets and tabular data

## Key Capabilities

| Feature | Description |
|---------|-------------|
| Smart Conversion | Automatically selects the best output format based on input type |
| OCR Processing | Extracts text from images using Tesseract |
| Base64 Encoding | Images are encoded for direct use in AI context windows |
| Batch Processing | Upload and convert multiple files at once |
| ZIP Download | Download all converted files in a single bundle |

## How It Works

1. **Upload** - Drag and drop files into the web interface
2. **Configure** - Optionally change the output format (Markdown or JSON)
3. **Convert** - Process all files with a single click
4. **Download** - Get individual files or a ZIP bundle

## Privacy & Security

- **No permanent storage** - Files are stored temporarily and auto-deleted after 15 minutes
- **Session isolation** - Each user's files are completely separate
- **Local processing** - All conversion happens on-server, no external API calls
- **Size limits** - 10MB per file, 50MB per session

## Technical Stack

- **Backend**: Python with FastAPI
- **OCR**: Tesseract
- **Deployment**: Docker-ready, cloud-compatible (Render, Railway, Fly.io)

## Use Cases

- Preparing documents for AI analysis or summarization
- Converting spreadsheet data into structured JSON for AI processing
- Extracting text from images and PDFs for chatbot context
- Batch-converting research materials for AI-assisted review
