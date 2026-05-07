# ⬡ PDF Tool

A lightweight desktop application for working with PDF files — built with Python, Tkinter and pypdf.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![pypdf](https://img.shields.io/badge/pypdf-6.x-green?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

---

## Features — 21 Tools

| Tool | Description |
|---|---|
| ➕ **Merge PDFs** | Combine multiple PDFs into one — drag & drop supported |
| ✂ **Split PDF** | Extract individual pages or a page range |
| 📄 **Extract Text** | Export text to TXT, DOCX or clipboard |
| 🖼 **Extract Images** | Save embedded images as PNG, JPG, TIFF or WebP |
| 🗜 **Compress** | Reduce file size by downsampling embedded images |
| 🔄 **Rotate** | Rotate pages 90°, 180° or 270° — all or specific pages |
| 💧 **Watermark** | Stamp text or image watermarks on any page |
| 🔒 **Password** | Add or remove PDF encryption |
| 🔀 **Reorder** | Drag pages into any order before saving |
| 🏷 **Metadata** | View and edit Title, Author, Subject, Keywords |
| 🗑 **Remove Blanks** | Detect and delete near-empty pages |
| 🔧 **Repair PDF** | Rebuild corrupted PDFs page by page |
| 🖼→📄 **Images to PDF** | Convert image files into a PDF document |
| ✂📐 **Crop Margins** | Trim page margins in mm (top / bottom / left / right) |
| 🔍 **OCR** | Extract text from scanned pages via Tesseract |
| ⚖ **Compare PDFs** | Side-by-side text diff with color-coded changes |
| ⬛ **Redact PDF** | Black out sensitive regions defined in mm |
| 🔢 **Page Numbers** | Add styled page numbers — position, format, color |
| ✍ **Signature** | Place a signature image on selected pages |
| 📄⊞ **N-Up** | Impose multiple pages per sheet (2-up, 4-up, 6-up, 9-up) |
| 🔖 **Bookmarks** | View, add, delete bookmarks — split PDF by chapter |

---

## Screenshot

> Dark-themed card navigation — click any tool to open it instantly.

```
┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
│  ➕      │  ✂       │  📄      │  🖼       │  🗜      │  🔄      │  💧      │
│  Merge   │  Split   │ Extract  │ Extract  │ Compress │  Rotate  │Watermark │
├──────────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│  🔒      │  🔀      │  🏷       │  🗑      │  🔧      │ 🖼→📄    │  ✂📐     │
│ Password │ Reorder  │ Metadata │  Remove  │  Repair  │  Images  │  Crop    │
├──────────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│  🔍      │  ⚖       │  ⬛      │  🔢      │  ✍       │  📄⊞     │  🔖      │
│   OCR    │ Compare  │  Redact  │  Page No │Signature │   N-Up   │Bookmarks │
└──────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘
```

---

## Installation

**1. Clone the repository**
```bash
git clone https://github.com/tvankov/pdf-tool.git
cd pdf-tool
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run the app**
```bash
python main.py
```

### Optional — Drag & Drop support
```bash
pip install tkinterdnd2
```

### Optional — OCR support
Install [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki). The app detects it automatically on Windows (`C:\Program Files\Tesseract-OCR\`).

---

## Download

> Don't want to run from source? Download the ready-to-use Windows executable:

👉 **[Download latest release](https://github.com/tvankov/pdf-tool/releases/latest)**

No Python installation required.

---

## Requirements

```
pypdf
reportlab
Pillow
python-docx
pdf2image
pytesseract
tkinterdnd2   # optional
```

---

## Project Structure

```
pdf_tool/
├── main.py           ← Entry point — card-based navigation
├── config.py         ← Color theme constants
├── requirements.txt
├── .gitignore
└── tabs/
    ├── __init__.py
    ├── merge.py          split.py          extract_text.py
    ├── extract_images.py compress.py       rotate.py
    ├── watermark.py      password.py       reorder.py
    ├── metadata.py       blank.py          repair.py
    ├── convert.py        crop.py           ocr.py
    ├── compare.py        redact.py         pagenumbers.py
    ├── signature.py      nup.py            bookmarks.py
```

### Adding a new tool

1. Create `tabs/your_feature.py` with a class `YourFeatureTab`
   — set `LABEL = "🔣  Tool Name"` (emoji + two spaces + name)
2. Register it in `tabs/__init__.py`
3. Add `YourFeatureTab` to `TAB_CLASSES` in `main.py`

---

## Author

**Todor Vankov** — 3D Artist & Developer transitioning into Data Analytics

🌐 [todorvankov.com](https://www.todorvankov.com) · 💼 [LinkedIn](https://www.linkedin.com/in/todorvankov)

---

## License

MIT — free to use and modify.
