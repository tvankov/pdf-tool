import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, filedialog
from datetime import datetime

from pypdf import PdfReader, PdfWriter
from config import BG, PANEL, ACCENT, ACCENT2, TEXT, SUBTEXT, DANGER, SUCCESS


FIELDS = [
    ("/Title",    "Title"),
    ("/Author",   "Author"),
    ("/Subject",  "Subject"),
    ("/Keywords", "Keywords"),
    ("/Creator",  "Creator"),
    ("/Producer", "Producer"),
]


class MetadataTab:
    """Tab — View and edit PDF metadata (title, author, subject, etc.)."""

    LABEL = "🏷  Metadata"

    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text=self.LABEL)
        self._build()

    def _build(self):
        f = self.frame

        tk.Label(f, text="View and edit PDF metadata — title, author, subject and more",
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

        # Metadata fields
        fields_frame = tk.Frame(f, bg=BG)
        fields_frame.pack(fill="x", padx=20, pady=(12, 4))

        self._vars = {}
        for key, label in FIELDS:
            row = tk.Frame(fields_frame, bg=BG)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=f"{label}:", bg=BG, fg=TEXT,
                     width=12, anchor="w").pack(side="left")
            var = tk.StringVar()
            self._vars[key] = var
            tk.Entry(row, textvariable=var, bg=PANEL, fg=TEXT,
                     insertbackground=TEXT, relief="flat",
                     font=("Segoe UI", 10), width=46).pack(side="left", padx=8)

        # Output file
        out_row = tk.Frame(f, bg=BG)
        out_row.pack(fill="x", padx=20, pady=(10, 4))
        tk.Label(out_row, text="Output file:", bg=BG, fg=TEXT).pack(side="left")
        self.out_var = tk.StringVar(
            value=os.path.join(os.path.expanduser("~/Desktop"), "output.pdf"))
        tk.Entry(out_row, textvariable=self.out_var, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=("Segoe UI", 10),
                 width=34).pack(side="left", padx=8)
        self._btn(out_row, "📁 Save as", self._pick_out, color="#334155").pack(side="left")

        # Run
        bot = tk.Frame(f, bg=BG)
        bot.pack(fill="x", padx=20, pady=(10, 12))
        self._btn(bot, "💾  Save Metadata", self._run, w=18).pack(side="left")
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
            self.out_var.set(os.path.join(os.path.dirname(path), base + "_meta.pdf"))
            try:
                reader = PdfReader(path)
                meta = reader.metadata or {}
                for key, _ in FIELDS:
                    self._vars[key].set(meta.get(key, ""))
            except Exception as e:
                self._set_status(f"Error reading metadata: {e}", ok=False)

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
            reader = PdfReader(src)
            writer = PdfWriter()
            writer.append(reader)
            meta = {k: v.get().strip() for k, v in self._vars.items() if v.get().strip()}
            meta["/ModDate"] = datetime.now().strftime("D:%Y%m%d%H%M%S")
            writer.add_metadata(meta)
            if not out.lower().endswith(".pdf"):
                out += ".pdf"
                self.out_var.set(out)
            with open(out, "wb") as fh:
                writer.write(fh)
            self._set_status(f"✓ Metadata saved  —  {os.path.basename(out)}")
            self.open_btn.pack(side="left", padx=8)
        except Exception as e:
            self._set_status(f"Error: {e}", ok=False)
            self.open_btn.pack_forget()
