import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, filedialog

from pypdf import PdfReader, PdfWriter
from config import BG, PANEL, ACCENT, ACCENT2, TEXT, SUBTEXT, DANGER, SUCCESS


class BlankTab:
    """Tab — Detect and remove blank pages from a PDF."""

    LABEL = "🗑  Remove Blanks"

    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text=self.LABEL)
        self._build()

    def _build(self):
        f = self.frame

        tk.Label(f, text="Detect and remove blank (empty) pages from a PDF",
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

        # Threshold
        thr_row = tk.Frame(f, bg=BG)
        thr_row.pack(fill="x", padx=20, pady=(14, 4))
        tk.Label(thr_row, text="Blank threshold:", bg=BG, fg=TEXT).pack(side="left")
        self.threshold_var = tk.IntVar(value=100)
        tk.Spinbox(thr_row, from_=1, to=2000, textvariable=self.threshold_var,
                   width=6, bg=PANEL, fg=TEXT, buttonbackground=PANEL,
                   relief="flat", font=("Segoe UI", 10)).pack(side="left", padx=8)
        tk.Label(thr_row,
                 text="characters  —  pages with fewer characters are considered blank",
                 bg=BG, fg=SUBTEXT, font=("Segoe UI", 9)).pack(side="left")

        # Preview box
        tk.Label(f, text="Detected blank pages:", bg=BG, fg=TEXT,
                 font=("Segoe UI", 10)).pack(anchor="w", padx=20, pady=(14, 4))

        preview_frame = tk.Frame(f, bg=PANEL, padx=2, pady=2)
        preview_frame.pack(fill="both", expand=True, padx=20, pady=(0, 6))
        self.preview = tk.Text(preview_frame, bg=PANEL, fg=TEXT,
                               font=("Consolas", 10), relief="flat",
                               state="disabled", height=6,
                               padx=10, pady=8, wrap="word")
        self.preview.pack(fill="both", expand=True)

        self._btn(f, "🔍  Scan for Blank Pages", self._scan, w=22
                  ).pack(anchor="w", padx=20, pady=(0, 6))

        # Output file
        out_row = tk.Frame(f, bg=BG)
        out_row.pack(fill="x", padx=20, pady=4)
        tk.Label(out_row, text="Output file:", bg=BG, fg=TEXT).pack(side="left")
        self.out_var = tk.StringVar(
            value=os.path.join(os.path.expanduser("~/Desktop"), "no_blanks.pdf"))
        tk.Entry(out_row, textvariable=self.out_var, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=("Segoe UI", 10),
                 width=34).pack(side="left", padx=8)
        self._btn(out_row, "📁 Save as", self._pick_out, color="#334155").pack(side="left")

        # Run
        bot = tk.Frame(f, bg=BG)
        bot.pack(fill="x", padx=20, pady=(6, 12))
        self._btn(bot, "🗑  Remove Blank Pages", self._run, w=20).pack(side="left")
        self.open_btn = self._btn(bot, "📂 Open folder", self._open_folder,
                                  color="#334155", w=14)
        self.open_btn.pack(side="left", padx=8)
        self.open_btn.pack_forget()
        self.status = tk.Label(bot, text="", bg=BG, font=("Segoe UI", 9))
        self.status.pack(side="left", padx=6)

        self._blank_pages = []

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

    def _set_preview(self, text):
        self.preview.config(state="normal")
        self.preview.delete("1.0", "end")
        self.preview.insert("end", text)
        self.preview.config(state="disabled")

    def _pick_src(self):
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if path:
            self.src_var.set(path)
            base = os.path.splitext(os.path.basename(path))[0]
            self.out_var.set(os.path.join(os.path.dirname(path), base + "_no_blanks.pdf"))
            self._blank_pages = []
            self._set_preview("")

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

    def _scan(self):
        src = self.src_var.get().strip()
        if not src:
            self._set_preview("Please select a PDF first.")
            return
        try:
            reader = PdfReader(src)
            threshold = self.threshold_var.get()
            self._blank_pages = []
            lines = []
            for i, page in enumerate(reader.pages):
                text = (page.extract_text() or "").strip()
                if len(text) < threshold:
                    self._blank_pages.append(i)
                    lines.append(f"  Page {i + 1}  —  {len(text)} characters")
            if self._blank_pages:
                self._set_preview(
                    f"Found {len(self._blank_pages)} blank page(s):\n" + "\n".join(lines))
            else:
                self._set_preview("✓ No blank pages found.")
        except Exception as e:
            self._set_preview(f"Error: {e}")

    def _run(self):
        src = self.src_var.get().strip()
        out = self.out_var.get().strip()
        if not src:
            self._set_status("⚠ Please select a source PDF!", ok=False)
            return
        if not self._blank_pages:
            self._set_status("⚠ Run Scan first!", ok=False)
            return
        try:
            reader = PdfReader(src)
            writer = PdfWriter()
            removed = 0
            for i, page in enumerate(reader.pages):
                if i not in self._blank_pages:
                    writer.add_page(page)
                else:
                    removed += 1
            if not out.lower().endswith(".pdf"):
                out += ".pdf"
                self.out_var.set(out)
            with open(out, "wb") as fh:
                writer.write(fh)
            self._set_status(f"✓ Removed {removed} blank page(s)  —  {os.path.basename(out)}")
            self.open_btn.pack(side="left", padx=8)
        except Exception as e:
            self._set_status(f"Error: {e}", ok=False)
            self.open_btn.pack_forget()
