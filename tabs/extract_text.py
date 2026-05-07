import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, filedialog

from pypdf import PdfReader
from config import BG, PANEL, ACCENT, ACCENT2, TEXT, SUBTEXT, DANGER, SUCCESS

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


class ExtractTextTab:
    """Tab — Extract text from a PDF and save as TXT, DOCX, and/or copy to clipboard."""

    LABEL = "📝  Extract Text"

    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text=self.LABEL)
        self._build()

    def _build(self):
        f = self.frame

        tk.Label(f, text="Extract text from a PDF — save as TXT, DOCX, or copy to clipboard",
                 bg=BG, fg=TEXT, font=("Segoe UI", 10, "bold")
                 ).pack(anchor="w", padx=20, pady=(16, 10))

        # Source file
        row1 = tk.Frame(f, bg=BG)
        row1.pack(fill="x", padx=20, pady=4)
        tk.Label(row1, text="Source PDF:", bg=BG, fg=TEXT).pack(side="left")
        self.src_var = tk.StringVar()
        tk.Entry(row1, textvariable=self.src_var, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=("Segoe UI", 10),
                 width=38).pack(side="left", padx=8)
        self._btn(row1, "📂 Open", self._pick_src, color="#334155").pack(side="left")

        # Pages
        tk.Label(f, text="Pages:", bg=BG, fg=TEXT,
                 font=("Segoe UI", 10)).pack(anchor="w", padx=20, pady=(12, 4))
        self.mode_var = tk.StringVar(value="all")
        tk.Radiobutton(f, text="All pages", variable=self.mode_var, value="all",
                       bg=BG, fg=TEXT, selectcolor=ACCENT, activebackground=BG,
                       font=("Segoe UI", 10)).pack(anchor="w", padx=36)
        tk.Radiobutton(f, text="Page range", variable=self.mode_var, value="range",
                       bg=BG, fg=TEXT, selectcolor=ACCENT, activebackground=BG,
                       font=("Segoe UI", 10)).pack(anchor="w", padx=36)

        row2 = tk.Frame(f, bg=BG)
        row2.pack(fill="x", padx=20, pady=(4, 2))
        tk.Label(row2, text="From:", bg=BG, fg=TEXT).pack(side="left", padx=(36, 0))
        self.from_var = tk.IntVar(value=1)
        tk.Spinbox(row2, from_=1, to=9999, textvariable=self.from_var,
                   width=5, bg=PANEL, fg=TEXT, buttonbackground=PANEL,
                   relief="flat", font=("Segoe UI", 10)).pack(side="left", padx=6)
        tk.Label(row2, text="To:", bg=BG, fg=TEXT).pack(side="left", padx=(10, 0))
        self.to_var = tk.IntVar(value=1)
        tk.Spinbox(row2, from_=1, to=9999, textvariable=self.to_var,
                   width=5, bg=PANEL, fg=TEXT, buttonbackground=PANEL,
                   relief="flat", font=("Segoe UI", 10)).pack(side="left", padx=6)

        # Format checkboxes — all on by default
        tk.Label(f, text="Output format:", bg=BG, fg=TEXT,
                 font=("Segoe UI", 10)).pack(anchor="w", padx=20, pady=(12, 4))

        self.fmt_txt  = tk.BooleanVar(value=True)
        self.fmt_docx = tk.BooleanVar(value=True)
        self.fmt_clip = tk.BooleanVar(value=True)

        fmt_row = tk.Frame(f, bg=BG)
        fmt_row.pack(anchor="w", padx=36)
        tk.Checkbutton(fmt_row, text="TXT", variable=self.fmt_txt,
                       bg=BG, fg=TEXT, selectcolor=PANEL, activebackground=BG,
                       font=("Segoe UI", 10)).pack(side="left", padx=(0, 16))
        self.docx_cb = tk.Checkbutton(fmt_row, text="DOCX (Word)", variable=self.fmt_docx,
                       bg=BG, fg=TEXT, selectcolor=PANEL, activebackground=BG,
                       font=("Segoe UI", 10))
        self.docx_cb.pack(side="left", padx=(0, 16))
        tk.Checkbutton(fmt_row, text="Clipboard", variable=self.fmt_clip,
                       bg=BG, fg=TEXT, selectcolor=PANEL, activebackground=BG,
                       font=("Segoe UI", 10)).pack(side="left")

        if not DOCX_AVAILABLE:
            self.fmt_docx.set(False)
            self.docx_cb.config(state="disabled")
            tk.Label(f, text="ℹ  DOCX requires: pip install python-docx",
                     bg=BG, fg=SUBTEXT, font=("Segoe UI", 8)
                     ).pack(anchor="w", padx=36, pady=(0, 2))

        # Output folder
        out_row = tk.Frame(f, bg=BG)
        out_row.pack(fill="x", padx=20, pady=(12, 4))
        tk.Label(out_row, text="Output folder:", bg=BG, fg=TEXT).pack(side="left")
        self.dir_var = tk.StringVar(value=os.path.expanduser("~/Desktop"))
        tk.Entry(out_row, textvariable=self.dir_var, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=("Segoe UI", 10),
                 width=34).pack(side="left", padx=8)
        self._btn(out_row, "📁", self._pick_dir, color="#334155").pack(side="left")

        # Run
        bot = tk.Frame(f, bg=BG)
        bot.pack(fill="x", padx=20, pady=(10, 12))
        self._btn(bot, "📝  Extract Text", self._run, w=18).pack(side="left")
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
            self.dir_var.set(os.path.dirname(path))

    def _pick_dir(self):
        d = filedialog.askdirectory(initialdir=self.dir_var.get())
        if d:
            self.dir_var.set(d)

    def _open_folder(self):
        d = os.path.abspath(self.dir_var.get())
        if sys.platform == "win32":
            subprocess.Popen(f'explorer "{d}"')
        elif sys.platform == "darwin":
            subprocess.Popen(["open", d])
        else:
            subprocess.Popen(["xdg-open", d])

    def _extract_text(self, reader):
        total = len(reader.pages)
        if self.mode_var.get() == "all":
            pages = range(total)
        else:
            pages = range(max(0, self.from_var.get() - 1),
                          min(total, self.to_var.get()))
        parts = [reader.pages[i].extract_text() or "" for i in pages]
        return "\n\n".join(p.strip() for p in parts), len(list(pages))

    # ── Actions ───────────────────────────────────────────────────────────────
    def _run(self):
        src = self.src_var.get().strip()
        if not src:
            self._set_status("⚠ Please select a source PDF!", ok=False)
            return

        want_txt  = self.fmt_txt.get()
        want_docx = self.fmt_docx.get()
        want_clip = self.fmt_clip.get()

        if not any([want_txt, want_docx, want_clip]):
            self._set_status("⚠ Select at least one output format!", ok=False)
            return

        try:
            reader = PdfReader(src)
            text, n_pages = self._extract_text(reader)

            if not text.strip():
                self._set_status("⚠ No text found (scanned PDF?)", ok=False)
                self.open_btn.pack_forget()
                return

            base = os.path.splitext(os.path.basename(src))[0]
            outdir = self.dir_var.get()
            saved = []

            if want_txt:
                out = os.path.join(outdir, base + ".txt")
                with open(out, "w", encoding="utf-8") as fh:
                    fh.write(text)
                saved.append("TXT")

            if want_docx:
                out = os.path.join(outdir, base + ".docx")
                doc = Document()
                for para in text.split("\n\n"):
                    doc.add_paragraph(para.strip())
                doc.save(out)
                saved.append("DOCX")

            if want_clip:
                self.frame.clipboard_clear()
                self.frame.clipboard_append(text)
                saved.append("Clipboard")

            saved_str = " + ".join(saved)
            self._set_status(f"✓ {saved_str}  —  {n_pages} page(s)")

            if want_txt or want_docx:
                self.open_btn.pack(side="left", padx=8)
            else:
                self.open_btn.pack_forget()

        except Exception as e:
            self._set_status(f"Error: {e}", ok=False)
            self.open_btn.pack_forget()
