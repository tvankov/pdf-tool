import os
import tkinter as tk
from tkinter import ttk, filedialog

from pypdf import PdfReader
from config import BG, PANEL, ACCENT, ACCENT2, TEXT, DANGER, SUCCESS


class InfoTab:
    """Tab 3 — Show metadata & page count of a PDF."""

    LABEL = "  ℹ  PDF Info  "

    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text=self.LABEL)
        self._build()

    def _build(self):
        f = self.frame

        tk.Label(f, text="Show metadata & page count of a PDF",
                 bg=BG, fg=TEXT, font=("Segoe UI", 10, "bold")
                 ).pack(anchor="w", padx=20, pady=(18, 12))

        row = tk.Frame(f, bg=BG)
        row.pack(fill="x", padx=20)
        self.src_var = tk.StringVar()
        tk.Entry(row, textvariable=self.src_var, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=("Segoe UI", 10),
                 width=46).pack(side="left", padx=(0, 8))
        self._btn(row, "📂 Open", self._pick_and_load, color="#334155").pack(side="left")

        self.info_box = tk.Text(f, bg=PANEL, fg=TEXT, font=("Consolas", 10),
                                relief="flat", state="disabled", height=12,
                                padx=14, pady=12, wrap="word",
                                insertbackground=TEXT)
        self.info_box.pack(fill="both", expand=True, padx=20, pady=14)

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

    def _pick_and_load(self):
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if path:
            self.src_var.set(path)
            self._load(path)

    def _load(self, src):
        try:
            reader = PdfReader(src)
            meta   = reader.metadata or {}
            lines  = [
                f"📄 File:      {os.path.basename(src)}",
                f"📑 Pages:     {len(reader.pages)}",
                f"📝 Title:     {meta.get('/Title',        '—')}",
                f"✍  Author:    {meta.get('/Author',       '—')}",
                f"🏷  Creator:   {meta.get('/Creator',      '—')}",
                f"📅 Created:   {meta.get('/CreationDate', '—')}",
                f"🔒 Encrypted: {'Yes' if reader.is_encrypted else 'No'}",
            ]
            content = "\n".join(lines)
        except Exception as e:
            content = f"Error: {e}"

        self.info_box.config(state="normal")
        self.info_box.delete("1.0", "end")
        self.info_box.insert("end", content)
        self.info_box.config(state="disabled")
