import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, filedialog

from config import BG, PANEL, ACCENT, ACCENT2, TEXT, SUBTEXT, DANGER, SUCCESS


_TESS_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    "/usr/bin/tesseract",
    "/usr/local/bin/tesseract",
]


def _set_tesseract_path():
    """Point pytesseract at the Tesseract binary if not already in PATH."""
    try:
        import pytesseract, shutil
        if not shutil.which("tesseract"):
            for p in _TESS_PATHS:
                if os.path.isfile(p):
                    pytesseract.pytesseract.tesseract_cmd = p
                    break
    except ImportError:
        pass


def _check_deps():
    """Return (pytesseract_ok, tesseract_binary_ok, pdf2image_ok)."""
    _set_tesseract_path()
    try:
        import pytesseract
        pt_ok = True
    except ImportError:
        pt_ok = False
    try:
        import pytesseract as _pt
        _pt.get_tesseract_version()
        tess_ok = True
    except Exception:
        tess_ok = False
    try:
        import pdf2image  # noqa
        p2i_ok = True
    except ImportError:
        p2i_ok = False
    return pt_ok, tess_ok, p2i_ok


class OcrTab:
    """Tab — Run OCR on a scanned PDF to make it text-searchable."""

    LABEL = "🔍  OCR"

    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text=self.LABEL)
        self._build()

    def _build(self):
        f = self.frame

        tk.Label(f, text="Make a scanned PDF text-searchable using OCR (Tesseract)",
                 bg=BG, fg=TEXT, font=("Segoe UI", 10, "bold")
                 ).pack(anchor="w", padx=20, pady=(16, 6))

        # Dependency check
        pt_ok, tess_ok, p2i_ok = _check_deps()
        all_ok = pt_ok and tess_ok and p2i_ok

        dep_frame = tk.Frame(f, bg=PANEL, padx=14, pady=10)
        dep_frame.pack(fill="x", padx=20, pady=(0, 12))
        tk.Label(dep_frame, text="Required dependencies:", bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        for label, ok, install in [
            ("pytesseract",     pt_ok,   "pip install pytesseract"),
            ("Tesseract binary", tess_ok, "https://github.com/UB-Mannheim/tesseract/wiki"),
            ("pdf2image",       p2i_ok,  "pip install pdf2image  (also needs poppler)"),
        ]:
            color = SUCCESS if ok else DANGER
            mark  = "✓" if ok else "✕"
            hint  = "" if ok else f"  →  {install}"
            tk.Label(dep_frame, text=f"  {mark}  {label}{hint}",
                     bg=PANEL, fg=color, font=("Segoe UI", 9)).pack(anchor="w")

        if not all_ok:
            tk.Label(f,
                     text="Install the missing dependencies above, then restart the app.",
                     bg=BG, fg=SUBTEXT, font=("Segoe UI", 9)
                     ).pack(anchor="w", padx=20, pady=(0, 8))

        # Source file
        row1 = tk.Frame(f, bg=BG)
        row1.pack(fill="x", padx=20, pady=4)
        tk.Label(row1, text="Source PDF:", bg=BG, fg=TEXT).pack(side="left")
        self.src_var = tk.StringVar()
        tk.Entry(row1, textvariable=self.src_var, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=("Segoe UI", 10),
                 width=36).pack(side="left", padx=8)
        self._btn(row1, "📂 Open", self._pick_src, color="#334155").pack(side="left")

        # Language
        lang_row = tk.Frame(f, bg=BG)
        lang_row.pack(fill="x", padx=20, pady=(10, 4))
        tk.Label(lang_row, text="Language:", bg=BG, fg=TEXT).pack(side="left")
        self.lang_var = tk.StringVar(value="eng")
        ttk.Combobox(lang_row, textvariable=self.lang_var, width=10, state="normal",
                     values=["eng", "deu", "fra", "spa", "ita",
                             "por", "nld", "pol", "rus", "chi_sim"]
                     ).pack(side="left", padx=8)
        tk.Label(lang_row, text="(Tesseract language code — must be installed)",
                 bg=BG, fg=SUBTEXT, font=("Segoe UI", 8)).pack(side="left")

        # DPI
        dpi_row = tk.Frame(f, bg=BG)
        dpi_row.pack(fill="x", padx=20, pady=(4, 4))
        tk.Label(dpi_row, text="Render DPI:", bg=BG, fg=TEXT).pack(side="left")
        self.dpi_var = tk.IntVar(value=300)
        tk.Spinbox(dpi_row, from_=72, to=600, textvariable=self.dpi_var,
                   width=5, bg=PANEL, fg=TEXT, buttonbackground=PANEL,
                   relief="flat", font=("Segoe UI", 10)).pack(side="left", padx=8)
        tk.Label(dpi_row, text="Higher = better accuracy, slower",
                 bg=BG, fg=SUBTEXT, font=("Segoe UI", 8)).pack(side="left")

        # Output file
        out_row = tk.Frame(f, bg=BG)
        out_row.pack(fill="x", padx=20, pady=(10, 4))
        tk.Label(out_row, text="Output file:", bg=BG, fg=TEXT).pack(side="left")
        self.out_var = tk.StringVar(
            value=os.path.join(os.path.expanduser("~/Desktop"), "ocr_output.pdf"))
        tk.Entry(out_row, textvariable=self.out_var, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=("Segoe UI", 10),
                 width=34).pack(side="left", padx=8)
        self._btn(out_row, "📁 Save as", self._pick_out, color="#334155").pack(side="left")

        # Run
        bot = tk.Frame(f, bg=BG)
        bot.pack(fill="x", padx=20, pady=(10, 12))
        run_btn = self._btn(bot, "🔍  Run OCR", self._run, w=14)
        if not all_ok:
            run_btn.config(state="disabled", bg="#334155")
        run_btn.pack(side="left")
        self.open_btn = self._btn(bot, "📂 Open folder", self._open_folder,
                                  color="#334155", w=14)
        self.open_btn.pack(side="left", padx=8)
        self.open_btn.pack_forget()
        self.status = tk.Label(bot, text="", bg=BG, font=("Segoe UI", 9))
        self.status.pack(side="left", padx=6)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _btn(self, parent, text, cmd, color=ACCENT, w=None):
        kw = dict(text=text, command=cmd, bg=color, fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat",
                  cursor="hand2", activebackground=ACCENT2,
                  activeforeground="white", pady=7, padx=14)
        if w:
            kw["width"] = w
        b = tk.Button(parent, **kw)
        b.bind("<Enter>", lambda e: b.config(bg=ACCENT2))
        b.bind("<Leave>", lambda e: b.config(bg=color))
        return b

    def _set_status(self, msg, ok=True):
        self.status.config(text=msg, fg=SUCCESS if ok else DANGER)

    def _pick_src(self):
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if path:
            self.src_var.set(path)
            base = os.path.splitext(os.path.basename(path))[0]
            self.out_var.set(os.path.join(os.path.dirname(path), base + "_ocr.pdf"))

    def _pick_out(self):
        path = filedialog.asksaveasfilename(
            initialdir=os.path.dirname(self.out_var.get()),
            initialfile=os.path.basename(self.out_var.get()),
            defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if path:
            self.out_var.set(path)

    def _open_folder(self):
        out = os.path.abspath(self.out_var.get())
        if sys.platform == "win32":
            subprocess.Popen(f'explorer /select,"{out}"')
        elif sys.platform == "darwin":
            subprocess.Popen(["open", os.path.dirname(out)])
        else:
            subprocess.Popen(["xdg-open", os.path.dirname(out)])

    def _run(self):
        src = self.src_var.get().strip()
        out = self.out_var.get().strip()
        if not src:
            self._set_status("⚠ Please select a source PDF!", ok=False)
            return
        try:
            _set_tesseract_path()
            import pytesseract
            from pdf2image import convert_from_path
            import io
            from pypdf import PdfWriter, PdfReader

            self._set_status("⏳ Converting pages to images…")
            self.frame.update()

            images = convert_from_path(src, dpi=self.dpi_var.get())
            lang   = self.lang_var.get().strip() or "eng"
            writer = PdfWriter()

            for i, img in enumerate(images):
                self._set_status(f"⏳ OCR page {i + 1}/{len(images)}…")
                self.frame.update()
                pdf_bytes = pytesseract.image_to_pdf_or_hocr(
                    img, extension="pdf", lang=lang)
                reader = PdfReader(io.BytesIO(pdf_bytes))
                writer.add_page(reader.pages[0])

            if not out.lower().endswith(".pdf"):
                out += ".pdf"
                self.out_var.set(out)
            with open(out, "wb") as fh:
                writer.write(fh)

            self._set_status(
                f"✓ OCR done — {len(images)} page(s)  —  {os.path.basename(out)}")
            self.open_btn.pack(side="left", padx=8)
        except Exception as e:
            self._set_status(f"Error: {e}", ok=False)
            self.open_btn.pack_forget()
