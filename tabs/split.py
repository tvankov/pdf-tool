import os
import tkinter as tk
from tkinter import ttk, filedialog

from pypdf import PdfWriter, PdfReader
from config import BG, PANEL, ACCENT, ACCENT2, TEXT, SUBTEXT, DANGER, SUCCESS


class SplitTab:
    """Tab 2 — Split a PDF into individual pages or a page range."""

    LABEL = "  ✂  Split PDF  "

    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text=self.LABEL)
        self._build()

    def _build(self):
        f = self.frame

        tk.Label(f, text="Split a PDF — save all pages individually or extract a range",
                 bg=BG, fg=TEXT, font=("Segoe UI", 10, "bold")
                 ).pack(anchor="w", padx=20, pady=(18, 12))

        # Source file
        row1 = tk.Frame(f, bg=BG)
        row1.pack(fill="x", padx=20, pady=4)
        tk.Label(row1, text="Source:", bg=BG, fg=TEXT).pack(side="left")
        self.src_var = tk.StringVar()
        tk.Entry(row1, textvariable=self.src_var, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=("Segoe UI", 10),
                 width=42).pack(side="left", padx=8)
        self._btn(row1, "📂 Open", self._pick_src, color="#334155").pack(side="left")

        # Mode
        tk.Label(f, text="Mode:", bg=BG, fg=TEXT,
                 font=("Segoe UI", 10)).pack(anchor="w", padx=20, pady=(14, 4))
        self.mode_var = tk.StringVar(value="all")
        for txt, val in [("Save every page as a separate file", "all"),
                         ("Extract a page range",               "range")]:
            tk.Radiobutton(f, text=txt, variable=self.mode_var, value=val,
                           bg=BG, fg=TEXT, selectcolor=ACCENT,
                           activebackground=BG,
                           font=("Segoe UI", 10)).pack(anchor="w", padx=36)

        # Page range
        row2 = tk.Frame(f, bg=BG)
        row2.pack(fill="x", padx=20, pady=10)
        tk.Label(row2, text="From page:", bg=BG, fg=TEXT).pack(side="left")
        self.from_var = tk.IntVar(value=1)
        tk.Spinbox(row2, from_=1, to=9999, textvariable=self.from_var,
                   width=5, bg=PANEL, fg=TEXT, buttonbackground=PANEL,
                   relief="flat", font=("Segoe UI", 10)).pack(side="left", padx=6)
        tk.Label(row2, text="To page:", bg=BG, fg=TEXT).pack(side="left", padx=(14, 0))
        self.to_var = tk.IntVar(value=1)
        tk.Spinbox(row2, from_=1, to=9999, textvariable=self.to_var,
                   width=5, bg=PANEL, fg=TEXT, buttonbackground=PANEL,
                   relief="flat", font=("Segoe UI", 10)).pack(side="left", padx=6)

        # Output folder
        row3 = tk.Frame(f, bg=BG)
        row3.pack(fill="x", padx=20, pady=4)
        tk.Label(row3, text="Output folder:", bg=BG, fg=TEXT).pack(side="left")
        self.dir_var = tk.StringVar(value=os.path.expanduser("~/Desktop"))
        tk.Entry(row3, textvariable=self.dir_var, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=("Segoe UI", 10),
                 width=32).pack(side="left", padx=8)
        self._btn(row3, "📁", lambda: self.dir_var.set(filedialog.askdirectory()),
                  color="#334155").pack(side="left")

        # Run
        bot = tk.Frame(f, bg=BG)
        bot.pack(fill="x", padx=20, pady=(16, 16))
        self._btn(bot, "✂  Split PDF", self._run, w=20).pack(side="left")
        self.status = tk.Label(bot, text="", bg=BG, font=("Segoe UI", 9))
        self.status.pack(side="left", padx=14)

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

    def _run(self):
        src    = self.src_var.get()
        outdir = self.dir_var.get()
        if not src:
            self._set_status("⚠ Please select a source file!", ok=False)
            return
        try:
            reader = PdfReader(src)
            total  = len(reader.pages)
            name   = os.path.splitext(os.path.basename(src))[0]
            pages  = range(total) if self.mode_var.get() == "all" else \
                     range(max(0, self.from_var.get() - 1),
                           min(total, self.to_var.get()))
            for i in pages:
                w = PdfWriter()
                w.add_page(reader.pages[i])
                with open(os.path.join(outdir, f"{name}_page{i+1}.pdf"), "wb") as fh:
                    w.write(fh)
            self._set_status(f"✓ {len(list(pages))} pages saved")
        except Exception as e:
            self._set_status(f"Error: {e}", ok=False)
