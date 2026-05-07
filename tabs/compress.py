import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, filedialog

from pypdf import PdfReader, PdfWriter
from config import BG, PANEL, ACCENT, ACCENT2, TEXT, SUBTEXT, DANGER, SUCCESS


class CompressTab:
    """Tab — Reduce PDF file size by compressing streams and removing redundant data."""

    LABEL = "🗜  Compress"

    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text=self.LABEL)
        self._build()

    def _build(self):
        f = self.frame

        tk.Label(f, text="Reduce PDF file size — compress streams and remove redundant data",
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

        # Size info
        self.size_label = tk.Label(f, text="", bg=BG, fg=SUBTEXT, font=("Segoe UI", 9))
        self.size_label.pack(anchor="w", padx=20, pady=(2, 0))

        # Options
        tk.Label(f, text="Options:", bg=BG, fg=TEXT,
                 font=("Segoe UI", 10)).pack(anchor="w", padx=20, pady=(14, 6))

        self.opt_streams  = tk.BooleanVar(value=True)
        self.opt_dupes    = tk.BooleanVar(value=True)
        self.opt_metadata = tk.BooleanVar(value=False)

        opts = [
            (self.opt_streams,  "Compress content streams",
             "Applies zlib compression to page content — biggest impact"),
            (self.opt_dupes,    "Remove duplicate objects",
             "Eliminates redundant objects shared across pages"),
            (self.opt_metadata, "Strip metadata",
             "Removes author, title, creation date, and other document info"),
        ]
        for var, label, hint in opts:
            row = tk.Frame(f, bg=BG)
            row.pack(anchor="w", padx=36, pady=2)
            tk.Checkbutton(row, text=label, variable=var,
                           bg=BG, fg=TEXT, selectcolor=PANEL, activebackground=BG,
                           font=("Segoe UI", 10)).pack(side="left")
            tk.Label(row, text=f"  —  {hint}", bg=BG, fg=SUBTEXT,
                     font=("Segoe UI", 9)).pack(side="left")

        # Output file
        out_row = tk.Frame(f, bg=BG)
        out_row.pack(fill="x", padx=20, pady=(16, 4))
        tk.Label(out_row, text="Output file:", bg=BG, fg=TEXT).pack(side="left")
        self.out_var = tk.StringVar(
            value=os.path.join(os.path.expanduser("~/Desktop"), "compressed.pdf"))
        tk.Entry(out_row, textvariable=self.out_var, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=("Segoe UI", 10),
                 width=34).pack(side="left", padx=8)
        self._btn(out_row, "📁 Save as", self._pick_out, color="#334155").pack(side="left")

        # Run
        bot = tk.Frame(f, bg=BG)
        bot.pack(fill="x", padx=20, pady=(12, 12))
        self._btn(bot, "🗜  Compress", self._run, w=16).pack(side="left")
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

    @staticmethod
    def _fmt_size(n_bytes):
        if n_bytes < 1024:
            return f"{n_bytes} B"
        if n_bytes < 1024 ** 2:
            return f"{n_bytes / 1024:.1f} KB"
        return f"{n_bytes / 1024 ** 2:.2f} MB"

    def _pick_src(self):
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if path:
            self.src_var.set(path)
            base = os.path.splitext(os.path.basename(path))[0]
            self.out_var.set(os.path.join(os.path.dirname(path), base + "_compressed.pdf"))
            size = os.path.getsize(path)
            self.size_label.config(text=f"File size: {self._fmt_size(size)}")

    def _pick_out(self):
        path = filedialog.asksaveasfilename(
            initialdir=os.path.dirname(self.out_var.get()),
            initialfile=os.path.basename(self.out_var.get()),
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")])
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

    # ── Actions ───────────────────────────────────────────────────────────────
    def _run(self):
        src = self.src_var.get().strip()
        out = self.out_var.get().strip()

        if not src:
            self._set_status("⚠ Please select a source PDF!", ok=False)
            return
        if not out:
            self._set_status("⚠ Please set an output file!", ok=False)
            return

        try:
            size_before = os.path.getsize(src)
            reader = PdfReader(src)
            writer = PdfWriter()

            for page in reader.pages:
                if self.opt_streams.get():
                    page.compress_content_streams()
                writer.add_page(page)

            if self.opt_dupes.get():
                writer.compress_identical_objects(
                    remove_identicals=True, remove_orphans=True)

            if not self.opt_metadata.get():
                writer.add_metadata(reader.metadata or {})

            if not out.lower().endswith(".pdf"):
                out += ".pdf"
                self.out_var.set(out)

            with open(out, "wb") as fh:
                writer.write(fh)

            size_after = os.path.getsize(out)
            saved_pct  = (1 - size_after / size_before) * 100 if size_before else 0

            self._set_status(
                f"✓  {self._fmt_size(size_before)} → {self._fmt_size(size_after)}"
                f"  ({saved_pct:+.1f}%)")
            self.open_btn.pack(side="left", padx=8)

        except Exception as e:
            self._set_status(f"Error: {e}", ok=False)
            self.open_btn.pack_forget()
