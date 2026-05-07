import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, filedialog

from pypdf import PdfReader, PdfWriter
from config import BG, PANEL, ACCENT, ACCENT2, TEXT, SUBTEXT, DANGER, SUCCESS


class CropTab:
    """Tab — Crop PDF pages by adjusting margins (in mm)."""

    LABEL = "✂📐  Crop Margins"

    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text=self.LABEL)
        self._build()

    def _build(self):
        f = self.frame

        tk.Label(f, text="Crop PDF pages by trimming margins — all pages or a range",
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

        self.info_lbl = tk.Label(f, text="", bg=BG, fg=SUBTEXT, font=("Segoe UI", 9))
        self.info_lbl.pack(anchor="w", padx=20, pady=(2, 0))

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

        range_row = tk.Frame(f, bg=BG)
        range_row.pack(fill="x", padx=20, pady=(4, 0))
        tk.Label(range_row, text="From:", bg=BG, fg=TEXT).pack(side="left", padx=(36, 0))
        self.from_var = tk.IntVar(value=1)
        tk.Spinbox(range_row, from_=1, to=9999, textvariable=self.from_var,
                   width=5, bg=PANEL, fg=TEXT, buttonbackground=PANEL,
                   relief="flat", font=("Segoe UI", 10)).pack(side="left", padx=6)
        tk.Label(range_row, text="To:", bg=BG, fg=TEXT).pack(side="left", padx=(10, 0))
        self.to_var = tk.IntVar(value=1)
        tk.Spinbox(range_row, from_=1, to=9999, textvariable=self.to_var,
                   width=5, bg=PANEL, fg=TEXT, buttonbackground=PANEL,
                   relief="flat", font=("Segoe UI", 10)).pack(side="left", padx=6)

        # Margin inputs (mm)
        tk.Label(f, text="Crop margins  (mm to remove from each side):",
                 bg=BG, fg=TEXT, font=("Segoe UI", 10)
                 ).pack(anchor="w", padx=20, pady=(16, 6))

        margins_frame = tk.Frame(f, bg=BG)
        margins_frame.pack(anchor="w", padx=36)
        self._margin_vars = {}
        for label, side in [("Top", "top"), ("Bottom", "bottom"),
                             ("Left", "left"), ("Right", "right")]:
            row = tk.Frame(margins_frame, bg=BG)
            row.pack(side="left", padx=(0, 20))
            tk.Label(row, text=label, bg=BG, fg=SUBTEXT,
                     font=("Segoe UI", 9)).pack()
            var = tk.DoubleVar(value=0.0)
            self._margin_vars[side] = var
            tk.Spinbox(row, from_=0, to=200, increment=1.0,
                       textvariable=var, format="%.1f",
                       width=6, bg=PANEL, fg=TEXT, buttonbackground=PANEL,
                       relief="flat", font=("Segoe UI", 10)).pack()

        tk.Label(f, text="Positive values trim inward. Negative values add white space.",
                 bg=BG, fg=SUBTEXT, font=("Segoe UI", 8)
                 ).pack(anchor="w", padx=36, pady=(4, 0))

        # Output file
        out_row = tk.Frame(f, bg=BG)
        out_row.pack(fill="x", padx=20, pady=(14, 4))
        tk.Label(out_row, text="Output file:", bg=BG, fg=TEXT).pack(side="left")
        self.out_var = tk.StringVar(
            value=os.path.join(os.path.expanduser("~/Desktop"), "cropped.pdf"))
        tk.Entry(out_row, textvariable=self.out_var, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=("Segoe UI", 10),
                 width=34).pack(side="left", padx=8)
        self._btn(out_row, "📁 Save as", self._pick_out, color="#334155").pack(side="left")

        # Run
        bot = tk.Frame(f, bg=BG)
        bot.pack(fill="x", padx=20, pady=(8, 12))
        self._btn(bot, "✂  Crop PDF", self._run, w=14).pack(side="left")
        self.open_btn = self._btn(bot, "📂 Open folder", self._open_folder,
                                  color="#334155", w=14)
        self.open_btn.pack(side="left", padx=8)
        self.open_btn.pack_forget()
        self.status = tk.Label(bot, text="", bg=BG, font=("Segoe UI", 9))
        self.status.pack(side="left", padx=6)

    # ── Helpers ───────────────────────────────────────────────────────────────
    MM_TO_PT = 2.8346

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
            self.out_var.set(os.path.join(os.path.dirname(path), base + "_cropped.pdf"))
            try:
                reader = PdfReader(path)
                p = reader.pages[0]
                w = float(p.mediabox.width)  / self.MM_TO_PT
                h = float(p.mediabox.height) / self.MM_TO_PT
                total = len(reader.pages)
                self.info_lbl.config(
                    text=f"{total} page(s)  —  page 1 size: {w:.1f} × {h:.1f} mm")
                self.to_var.set(total)
            except Exception:
                self.info_lbl.config(text="")

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

        top    = self._margin_vars["top"].get()    * self.MM_TO_PT
        bottom = self._margin_vars["bottom"].get() * self.MM_TO_PT
        left   = self._margin_vars["left"].get()   * self.MM_TO_PT
        right  = self._margin_vars["right"].get()  * self.MM_TO_PT

        try:
            reader = PdfReader(src)
            total  = len(reader.pages)
            writer = PdfWriter()

            if self.mode_var.get() == "all":
                crop_indices = set(range(total))
            else:
                crop_indices = set(range(
                    max(0, self.from_var.get() - 1),
                    min(total, self.to_var.get())))

            for i, page in enumerate(reader.pages):
                if i in crop_indices:
                    mb = page.mediabox
                    x0 = float(mb.left)   + left
                    y0 = float(mb.bottom) + bottom
                    x1 = float(mb.right)  - right
                    y1 = float(mb.top)    - top
                    page.mediabox.left   = x0
                    page.mediabox.bottom = y0
                    page.mediabox.right  = x1
                    page.mediabox.top    = y1
                writer.add_page(page)

            if not out.lower().endswith(".pdf"):
                out += ".pdf"
                self.out_var.set(out)
            with open(out, "wb") as fh:
                writer.write(fh)
            self._set_status(
                f"✓ Cropped {len(crop_indices)} page(s)  —  {os.path.basename(out)}")
            self.open_btn.pack(side="left", padx=8)
        except Exception as e:
            self._set_status(f"Error: {e}", ok=False)
            self.open_btn.pack_forget()
