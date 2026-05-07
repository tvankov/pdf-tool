import io
import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, filedialog

from pypdf import PdfReader
from config import BG, PANEL, ACCENT, ACCENT2, TEXT, SUBTEXT, DANGER, SUCCESS

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class ExtractImagesTab:
    """Tab — Extract all images from a PDF and save as PNG and/or JPG."""

    LABEL = "🖼  Extract Images"

    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text=self.LABEL)
        self._build()

    def _build(self):
        f = self.frame

        tk.Label(f, text="Extract all images from a PDF — save as PNG and/or JPG",
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

        self.fmt_png  = tk.BooleanVar(value=True)
        self.fmt_jpg  = tk.BooleanVar(value=True)
        self.fmt_tiff = tk.BooleanVar(value=True)
        self.fmt_webp = tk.BooleanVar(value=True)

        fmt_row = tk.Frame(f, bg=BG)
        fmt_row.pack(anchor="w", padx=36)
        for label, var in [("PNG", self.fmt_png), ("JPG", self.fmt_jpg),
                            ("TIFF", self.fmt_tiff), ("WebP", self.fmt_webp)]:
            tk.Checkbutton(fmt_row, text=label, variable=var,
                           bg=BG, fg=TEXT, selectcolor=PANEL, activebackground=BG,
                           font=("Segoe UI", 10)).pack(side="left", padx=(0, 16))

        # JPG quality
        qual_row = tk.Frame(f, bg=BG)
        qual_row.pack(fill="x", padx=20, pady=(6, 2))
        tk.Label(qual_row, text="JPG quality:", bg=BG, fg=TEXT).pack(side="left", padx=(36, 0))
        self.quality_var = tk.IntVar(value=85)
        tk.Spinbox(qual_row, from_=10, to=100, textvariable=self.quality_var,
                   width=4, bg=PANEL, fg=TEXT, buttonbackground=PANEL,
                   relief="flat", font=("Segoe UI", 10)).pack(side="left", padx=6)
        tk.Label(qual_row, text="(10–100)", bg=BG, fg=SUBTEXT,
                 font=("Segoe UI", 9)).pack(side="left")

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
        self._btn(bot, "🖼  Extract Images", self._run, w=18).pack(side="left")
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

    # ── Actions ───────────────────────────────────────────────────────────────
    def _run(self):
        src = self.src_var.get().strip()
        if not src:
            self._set_status("⚠ Please select a source PDF!", ok=False)
            return

        want_png  = self.fmt_png.get()
        want_jpg  = self.fmt_jpg.get()
        want_tiff = self.fmt_tiff.get()
        want_webp = self.fmt_webp.get()

        if not any([want_png, want_jpg, want_tiff, want_webp]):
            self._set_status("⚠ Select at least one output format!", ok=False)
            return

        try:
            reader  = PdfReader(src)
            total   = len(reader.pages)
            base    = os.path.splitext(os.path.basename(src))[0]
            outdir  = self.dir_var.get()
            quality = self.quality_var.get()

            if self.mode_var.get() == "all":
                pages = range(total)
            else:
                pages = range(max(0, self.from_var.get() - 1),
                              min(total, self.to_var.get()))

            count = 0
            for page_num in pages:
                page = reader.pages[page_num]
                for img_num, img_obj in enumerate(page.images, start=1):
                    raw = img_obj.data
                    stem = f"{base}_p{page_num + 1}_img{img_num}"

                    pil_img = Image.open(io.BytesIO(raw))

                    if want_png:
                        pil_img.convert("RGBA").save(
                            os.path.join(outdir, stem + ".png"), "PNG")
                    if want_jpg:
                        pil_img.convert("RGB").save(
                            os.path.join(outdir, stem + ".jpg"), "JPEG",
                            quality=quality)
                    if want_tiff:
                        pil_img.convert("RGBA").save(
                            os.path.join(outdir, stem + ".tiff"), "TIFF")
                    if want_webp:
                        pil_img.convert("RGBA").save(
                            os.path.join(outdir, stem + ".webp"), "WEBP",
                            quality=quality)

                    count += 1

            if count == 0:
                self._set_status("⚠ No images found in the selected pages", ok=False)
                self.open_btn.pack_forget()
            else:
                fmts = " + ".join(f for f, v in [
                    ("PNG", want_png), ("JPG", want_jpg),
                    ("TIFF", want_tiff), ("WebP", want_webp)] if v)
                self._set_status(f"✓ {count} image(s) saved  —  {fmts}")
                self.open_btn.pack(side="left", padx=8)

        except Exception as e:
            self._set_status(f"Error: {e}", ok=False)
            self.open_btn.pack_forget()
