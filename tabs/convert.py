import os
import re
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, filedialog

from PIL import Image
from pypdf import PdfWriter
from config import BG, PANEL, ACCENT, ACCENT2, TEXT, SUBTEXT, DANGER, SUCCESS, DROP_BG

try:
    from tkinterdnd2 import DND_FILES
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False


class ConvertTab:
    """Tab — Combine images (JPG, PNG, WebP, TIFF, BMP) into a single PDF."""

    LABEL = "🖼→📄  Images to PDF"

    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text=self.LABEL)
        self._build()

    def _build(self):
        f = self.frame

        tk.Label(f, text="Combine images into a PDF — drag & drop or use the buttons",
                 bg=BG, fg=TEXT, font=("Segoe UI", 10, "bold")
                 ).pack(anchor="w", padx=20, pady=(16, 6))

        # Drop zone / list
        drop_outer = tk.Frame(f, bg=ACCENT, padx=2, pady=2)
        drop_outer.pack(fill="both", expand=True, padx=20, pady=(0, 4))
        drop_inner = tk.Frame(drop_outer, bg=DROP_BG)
        drop_inner.pack(fill="both", expand=True)

        self.hint = tk.Label(drop_inner,
                             text="⬇   Drop image files here  (JPG · PNG · WebP · TIFF · BMP)",
                             bg=DROP_BG, fg=SUBTEXT, font=("Segoe UI", 11))

        sb = ttk.Scrollbar(drop_inner, orient="vertical")
        self.listbox = tk.Listbox(
            drop_inner, bg=DROP_BG, fg=TEXT,
            selectbackground=ACCENT, selectforeground="white",
            font=("Segoe UI", 10), relief="flat", bd=0,
            activestyle="none", height=6, yscrollcommand=sb.set)
        sb.config(command=self.listbox.yview)
        self.listbox.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        sb.pack(side="right", fill="y", pady=6)
        self.hint.place(relx=0.5, rely=0.5, anchor="center")

        if DND_AVAILABLE:
            for w in (drop_inner, self.listbox, self.hint):
                w.drop_target_register(DND_FILES)
                w.dnd_bind("<<Drop>>", self._on_drop)

        # Buttons
        btn_row = tk.Frame(f, bg=BG)
        btn_row.pack(fill="x", padx=20, pady=4)
        self._btn(btn_row, "+ Add Images", self._add).pack(side="left", padx=(0, 6))
        self._btn(btn_row, "↑ Up",         self._up,     color="#334155").pack(side="left", padx=(0, 6))
        self._btn(btn_row, "↓ Down",       self._down,   color="#334155").pack(side="left", padx=(0, 6))
        self._btn(btn_row, "✕ Remove",     self._remove, color=DANGER   ).pack(side="left", padx=(0, 6))
        self._btn(btn_row, "🗑 Clear All",  self._clear,  color="#334155").pack(side="left")

        # Page size option
        size_row = tk.Frame(f, bg=BG)
        size_row.pack(fill="x", padx=20, pady=(4, 2))
        tk.Label(size_row, text="Page size:", bg=BG, fg=TEXT).pack(side="left")
        self.size_var = tk.StringVar(value="Image size")
        ttk.Combobox(size_row, textvariable=self.size_var, state="readonly", width=14,
                     values=["Image size", "A4 portrait", "A4 landscape",
                             "Letter portrait", "Letter landscape"]
                     ).pack(side="left", padx=8)

        # Output file
        out_row = tk.Frame(f, bg=BG)
        out_row.pack(fill="x", padx=20, pady=(4, 4))
        tk.Label(out_row, text="Output file:", bg=BG, fg=TEXT).pack(side="left")
        self.out_var = tk.StringVar(
            value=os.path.join(os.path.expanduser("~/Desktop"), "images.pdf"))
        tk.Entry(out_row, textvariable=self.out_var, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=("Segoe UI", 10),
                 width=32).pack(side="left", padx=8)
        self._btn(out_row, "📁 Save as", self._pick_out, color="#334155").pack(side="left")

        # Run
        bot = tk.Frame(f, bg=BG)
        bot.pack(fill="x", padx=20, pady=(4, 10))
        self._btn(bot, "📄  Convert to PDF", self._run, w=18).pack(side="left")
        self.open_btn = self._btn(bot, "📂 Open folder", self._open_folder,
                                  color="#334155", w=14)
        self.open_btn.pack(side="left", padx=8)
        self.open_btn.pack_forget()
        self.status = tk.Label(bot, text="", bg=BG, font=("Segoe UI", 9))
        self.status.pack(side="left", padx=6)

        if not DND_AVAILABLE:
            tk.Label(f, bg=BG, fg=SUBTEXT, font=("Segoe UI", 8),
                     text="ℹ  For drag & drop: pip install tkinterdnd2"
                     ).pack(anchor="w", padx=22)

    # ── Helpers ───────────────────────────────────────────────────────────────
    IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif", ".bmp"}

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

    def _hint_update(self):
        self.hint.lift() if self.listbox.size() == 0 else self.hint.lower()

    def _on_drop(self, event):
        paths = re.findall(r'\{([^}]+)\}', event.data)
        plain = re.sub(r'\{[^}]+\}', '', event.data).strip()
        if plain:
            paths += plain.split()
        added = 0
        for p in paths:
            p = p.strip()
            if os.path.splitext(p)[1].lower() in self.IMG_EXTS and os.path.isfile(p):
                self.listbox.insert("end", p)
                added += 1
        self._set_status(f"✓ {added} image(s) added" if added else "⚠ No valid images dropped",
                         ok=bool(added))
        self._hint_update()

    def _add(self):
        for p in filedialog.askopenfilenames(
                filetypes=[("Image Files", "*.jpg *.jpeg *.png *.webp *.tiff *.tif *.bmp")]):
            self.listbox.insert("end", p)
        self._hint_update()

    def _remove(self):
        for i in reversed(self.listbox.curselection()):
            self.listbox.delete(i)
        self._hint_update()

    def _clear(self):
        self.listbox.delete(0, "end")
        self._hint_update()

    def _up(self):
        sel = self.listbox.curselection()
        if not sel or sel[0] == 0:
            return
        i, v = sel[0], self.listbox.get(sel[0])
        self.listbox.delete(i)
        self.listbox.insert(i - 1, v)
        self.listbox.select_set(i - 1)

    def _down(self):
        sel = self.listbox.curselection()
        if not sel or sel[0] == self.listbox.size() - 1:
            return
        i, v = sel[0], self.listbox.get(sel[0])
        self.listbox.delete(i)
        self.listbox.insert(i + 1, v)
        self.listbox.select_set(i + 1)

    def _pick_out(self):
        path = filedialog.asksaveasfilename(
            initialdir=os.path.expanduser("~/Desktop"),
            initialfile="images.pdf",
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

    # ── Page size presets (in points: 1pt = 1/72 inch) ───────────────────────
    PAGE_SIZES = {
        "A4 portrait":      (595, 842),
        "A4 landscape":     (842, 595),
        "Letter portrait":  (612, 792),
        "Letter landscape": (792, 612),
    }

    def _run(self):
        files = list(self.listbox.get(0, "end"))
        if not files:
            self._set_status("⚠ Add at least one image!", ok=False)
            return
        out = self.out_var.get().strip()
        preset = self.size_var.get()
        try:
            from reportlab.pdfgen import canvas as rl_canvas
            import io
            from pypdf import PdfReader

            buf = io.BytesIO()
            page_size = self.PAGE_SIZES.get(preset)

            if page_size:
                pw, ph = page_size
                c = rl_canvas.Canvas(buf, pagesize=(pw, ph))
                for path in files:
                    with Image.open(path) as img:
                        iw, ih = img.size
                    scale = min(pw / iw, ph / ih)
                    dw, dh = iw * scale, ih * scale
                    x, y   = (pw - dw) / 2, (ph - dh) / 2
                    c.drawImage(path, x, y, width=dw, height=dh)
                    c.showPage()
            else:
                # Use each image's natural size
                first = True
                c = None
                for path in files:
                    with Image.open(path) as img:
                        iw, ih = img.size
                    if first:
                        c = rl_canvas.Canvas(buf, pagesize=(iw, ih))
                        first = False
                    else:
                        c.setPageSize((iw, ih))
                    c.drawImage(path, 0, 0, width=iw, height=ih)
                    c.showPage()

            c.save()
            buf.seek(0)

            if not out.lower().endswith(".pdf"):
                out += ".pdf"
                self.out_var.set(out)

            with open(out, "wb") as fh:
                fh.write(buf.read())

            self._set_status(f"✓ {len(files)} image(s) → {os.path.basename(out)}")
            self.open_btn.pack(side="left", padx=8)
        except Exception as e:
            self._set_status(f"Error: {e}", ok=False)
            self.open_btn.pack_forget()
