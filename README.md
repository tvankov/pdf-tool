# ⬡ PDF Tool

A lightweight desktop application for working with PDF files — built with Python, Tkinter and pypdf.

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![pypdf](https://img.shields.io/badge/pypdf-4.x-green?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

---

## Features

| Tab | Description |
|---|---|
| ➕ **Merge PDFs** | Combine multiple PDFs into one — drag & drop supported |
| ✂ **Split PDF** | Extract individual pages or a specific page range |
| ℹ **PDF Info** | Display metadata, page count and encryption status |

---

## Preview

> Dark-themed desktop UI with tab-based navigation and drag & drop support.

<img width="923" height="773" alt="grafik" src="https://github.com/user-attachments/assets/77289f04-6a38-43e9-a5ed-4ae2d1fad43f" />

<img width="926" height="775" alt="grafik" src="https://github.com/user-attachments/assets/6da2758c-08a7-4473-bad7-71448aa89b9d" />

<img width="924" height="773" alt="grafik" src="https://github.com/user-attachments/assets/6ca4cb44-f3f7-4217-81b8-ab4844d277ce" />

---

## Installation

**1. Clone the repository**
```bash
git clone https://github.com/tvankov/pdf-tool.git
cd pdf-tool
```

**2. Create a virtual environment**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
pip install tkinterdnd2      # optional — enables drag & drop
```

**4. Run the app**
```bash
python main.py
```

---

## Download

> Don't want to run from source? Download the ready-to-use Windows executable:

👉 **[Download latest release](https://github.com/tvankov/pdf-tool/releases/latest)**

No Python installation required.

---

## Project Structure

```
pdf_tool/
├── main.py          ← Entry point — launches the app
├── config.py        ← Color theme and shared constants
├── requirements.txt
├── .gitignore
└── tabs/
    ├── __init__.py  ← Imports all tab classes
    ├── merge.py     ← Merge PDFs tab
    ├── split.py     ← Split PDF tab
    └── info.py      ← PDF Info tab
```

### Adding a new tab

1. Create `tabs/your_feature.py` with a class `YourFeatureTab`
2. Register it in `tabs/__init__.py`
3. Add one line in `main.py` inside `_build_tabs()`:

```python
YourFeatureTab(nb)
```

---

## Roadmap

- [ ] 🔒 Encrypt / Decrypt PDF
- [ ] 🔄 Rotate pages
- [ ] 🖼 Extract images from PDF
- [ ] 💧 Add watermark
- [ ] 📝 Fill PDF forms

---

## Author

**Todor Vankov** — 3D Artist & Developer transitioning into Data Analytics

🌐 [todorvankov.com](https://www.todorvankov.com) · 💼 [LinkedIn](https://www.linkedin.com/in/todorvankov)

---

## License

MIT — free to use and modify.
