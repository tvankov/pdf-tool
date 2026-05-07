import io
import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, filedialog

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.colors import Color as RLColor
from config import BG, PANEL, ACCENT, ACCENT2, TEXT, SUBTEXT, DANGER, SUCCESS


COLORS = {
    "Gray":  (0.5, 0.5, 0.5),
    "Black": (0.0, 0.0, 0.0),
    "White": (1.0, 1.0, 1.0),
    "Red":   (0.8, 0.1, 0.1),
    "Blue":  (0.1, 0.3, 0.8),
}


class WatermarkTab:
    """Tab — Stamp a text or image watermark on every page of a PDF."""

    LABEL = "💧  Watermark"

    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text=self.LABEL)
        self._build()

    def _build(self):
        f = self.frame

        tk.Label(f, text="Add a text or image watermark to every page of a PDF",
                 bg=BG, fg=TEXT, font=("Segoe UI", 10, "bold")
                 ).pack(anchor="w", padx=20, pady=(16, 10))

        # Source file
        row1 = tk.Frame(f, bg=BG)
        row1.pack(fill="x", padx=20, pady=4)
        tk.Label(row1, text="Source PDF:", bg=BG, fg=TEXT).pack(side="left")
        self.src_var = tk.StringVar()
        tk.Entry(row1, textvariable=self.src_var, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=("Segoe UI", 10),
                 width=36).pack(side="left", padx=8)
        self._btn(row1, "📂 Open", self._pick_src, color="#334155").pack(side="left")

        # Mode toggle
        tk.Label(f, text="Watermark type:", bg=BG, fg=TEXT,
                 font=("Segoe UI", 10)).pack(anchor="w", padx=20, pady=(12, 4))
        self.mode_var = tk.StringVar(value="text")
        mode_row = tk.Frame(f, bg=BG)
        mode_row.pack(anchor="w", padx=36)
        tk.Radiobutton(mode_row, text="Text", variable=self.mode_var, value="text",
                       bg=BG, fg=TEXT, selectcolor=ACCENT, activebackground=BG,
                       font=("Segoe UI", 10), command=self._on_mode).pack(side="left", padx=(0, 20))
        tk.Radiobutton(mode_row, text="Image", variable=self.mode_var, value="image",
                       bg=BG, fg=TEXT, selectcolor=ACCENT, activebackground=BG,
                       font=("Segoe UI", 10), command=self._on_mode).pack(side="left")

        # ── Text section ──────────────────────────────────────────────────────
        self.text_frame = tk.Frame(f, bg=BG)
        self.text_frame.pack(fill="x", padx=20, pady=(6, 0))

        tr1 = tk.Frame(self.text_frame, bg=BG)
        tr1.pack(fill="x", pady=3)
        tk.Label(tr1, text="Text:", bg=BG, fg=TEXT, width=10, anchor="w").pack(side="left", padx=(16, 0))
        self.wm_text = tk.StringVar(value="CONFIDENTIAL")
        tk.Entry(tr1, textvariable=self.wm_text, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=("Segoe UI", 10),
                 width=28).pack(side="left", padx=8)

        tr2 = tk.Frame(self.text_frame, bg=BG)
        tr2.pack(fill="x", pady=3)
        tk.Label(tr2, text="Font size:", bg=BG, fg=TEXT, width=10, anchor="w").pack(side="left", padx=(16, 0))
        self.font_size = tk.IntVar(value=60)
        tk.Spinbox(tr2, from_=10, to=200, textvariable=self.font_size,
                   width=5, bg=PANEL, fg=TEXT, buttonbackground=PANEL,
                   relief="flat", font=("Segoe UI", 10)).pack(side="left", padx=8)
        tk.Label(tr2, text="Color:", bg=BG, fg=TEXT).pack(side="left", padx=(20, 6))
        self.color_var = tk.StringVar(value="Gray")
        ttk.Combobox(tr2, textvariable=self.color_var,
                     values=list(COLORS.keys()), width=8,
                     state="readonly").pack(side="left")

        tr3 = tk.Frame(self.text_frame, bg=BG)
        tr3.pack(fill="x", pady=3)
        tk.Label(tr3, text="Angle:", bg=BG, fg=TEXT, width=10, anchor="w").pack(side="left", padx=(16, 0))
        self.angle_var = tk.IntVar(value=45)
        for lbl, val in [("Diagonal (45°)", 45), ("Horizontal (0°)", 0), ("Vertical (90°)", 90)]:
            tk.Radiobutton(tr3, text=lbl, variable=self.angle_var, value=val,
                           bg=BG, fg=TEXT, selectcolor=ACCENT, activebackground=BG,
                           font=("Segoe UI", 10)).pack(side="left", padx=(0, 14))

        # ── Image section ─────────────────────────────────────────────────────
        self.image_frame = tk.Frame(f, bg=BG)
        self.image_frame.pack(fill="x", padx=20, pady=(6, 0))

        ir1 = tk.Frame(self.image_frame, bg=BG)
        ir1.pack(fill="x", pady=3)
        tk.Label(ir1, text="Image:", bg=BG, fg=TEXT, width=10, anchor="w").pack(side="left", padx=(16, 0))
        self.img_var = tk.StringVar()
        tk.Entry(ir1, textvariable=self.img_var, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=("Segoe UI", 10),
                 width=28).pack(side="left", padx=8)
        self._btn(ir1, "📂", self._pick_img, color="#334155").pack(side="left")

        ir2 = tk.Frame(self.image_frame, bg=BG)
        ir2.pack(fill="x", pady=3)
        tk.Label(ir2, text="Scale:", bg=BG, fg=TEXT, width=10, anchor="w").pack(side="left", padx=(16, 0))
        self.img_scale = tk.IntVar(value=50)
        tk.Spinbox(ir2, from_=5, to=100, textvariable=self.img_scale,
                   width=4, bg=PANEL, fg=TEXT, buttonbackground=PANEL,
                   relief="flat", font=("Segoe UI", 10)).pack(side="left", padx=6)
        tk.Label(ir2, text="% of page width", bg=BG, fg=SUBTEXT,
                 font=("Segoe UI", 9)).pack(side="left")

        # ── Shared: opacity ───────────────────────────────────────────────────
        op_row = tk.Frame(f, bg=BG)
        op_row.pack(fill="x", padx=20, pady=(8, 4))
        tk.Label(op_row, text="Opacity:", bg=BG, fg=TEXT, width=10, anchor="w").pack(side="left", padx=(36, 0))
        self.opacity_var = tk.IntVar(value=30)
        tk.Scale(op_row, from_=5, to=100, orient="horizontal",
                 variable=self.opacity_var, bg=BG, fg=TEXT,
                 troughcolor=PANEL, highlightthickness=0,
                 length=180).pack(side="left", padx=6)
        tk.Label(op_row, text="%", bg=BG, fg=SUBTEXT, font=("Segoe UI", 9)).pack(side="left")

        # Output file
        out_row = tk.Frame(f, bg=BG)
        out_row.pack(fill="x", padx=20, pady=(10, 4))
        tk.Label(out_row, text="Output file:", bg=BG, fg=TEXT).pack(side="left")
        self.out_var = tk.StringVar(
            value=os.path.join(os.path.expanduser("~/Desktop"), "watermarked.pdf"))
        tk.Entry(out_row, textvariable=self.out_var, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=("Segoe UI", 10),
                 width=34).pack(side="left", padx=8)
        self._btn(out_row, "📁 Save as", self._pick_out, color="#334155").pack(side="left")

        # Run
        bot = tk.Frame(f, bg=BG)
        bot.pack(fill="x", padx=20, pady=(10, 12))
        self._btn(bot, "💧  Apply Watermark", self._run, w=20).pack(side="left")
        self.open_btn = self._btn(bot, "📂 Open folder", self._open_folder,
                                  color="#334155", w=14)
        self.open_btn.pack(side="left", padx=8)
        self.open_btn.pack_forget()
        self.status = tk.Label(bot, text="", bg=BG, font=("Segoe UI", 9))
        self.status.pack(side="left", padx=6)

        self._on_mode()

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

    def _on_mode(self):
        is_text = self.mode_var.get() == "text"
        self.text_frame.pack(fill="x", padx=20, pady=(6, 0)) if is_text else self.text_frame.pack_forget()
        self.image_frame.pack(fill="x", padx=20, pady=(6, 0)) if not is_text else self.image_frame.pack_forget()

    def _pick_src(self):
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if path:
            self.src_var.set(path)
            base = os.path.splitext(os.path.basename(path))[0]
            self.out_var.set(os.path.join(os.path.dirname(path), base + "_watermarked.pdf"))

    def _pick_img(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.webp"), ("All Files", "*.*")])
        if path:
            self.img_var.set(path)

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

    def _make_text_watermark(self, width, height):
        alpha   = self.opacity_var.get() / 100
        r, g, b = COLORS.get(self.color_var.get(), (0.5, 0.5, 0.5))
        buf     = io.BytesIO()
        c       = rl_canvas.Canvas(buf, pagesize=(width, height))
        c.setFillColor(RLColor(r, g, b, alpha))
        c.setFont("Helvetica-Bold", self.font_size.get())
        c.saveState()
        c.translate(width / 2, height / 2)
        c.rotate(self.angle_var.get())
        c.drawCentredString(0, 0, self.wm_text.get())
        c.restoreState()
        c.save()
        buf.seek(0)
        return PdfReader(buf).pages[0]

    def _make_image_watermark(self, width, height):
        alpha     = self.opacity_var.get() / 100
        scale     = self.img_scale.get() / 100
        img_path  = self.img_var.get()
        from PIL import Image as PILImage
        with PILImage.open(img_path) as img:
            iw, ih = img.size
        draw_w = width * scale
        draw_h = ih * (draw_w / iw)
        x = (width  - draw_w) / 2
        y = (height - draw_h) / 2
        buf = io.BytesIO()
        c   = rl_canvas.Canvas(buf, pagesize=(width, height))
        c.saveState()
        c.setFillAlpha(alpha)
        c.drawImage(img_path, x, y, width=draw_w, height=draw_h, mask="auto")
        c.restoreState()
        c.save()
        buf.seek(0)
        return PdfReader(buf).pages[0]

    # ── Actions ───────────────────────────────────────────────────────────────
    def _run(self):
        src = self.src_var.get().strip()
        out = self.out_var.get().strip()

        if not src:
            self._set_status("⚠ Please select a source PDF!", ok=False)
            return
        if self.mode_var.get() == "text" and not self.wm_text.get().strip():
            self._set_status("⚠ Please enter watermark text!", ok=False)
            return
        if self.mode_var.get() == "image" and not self.img_var.get().strip():
            self._set_status("⚠ Please select a watermark image!", ok=False)
            return

        try:
            reader = PdfReader(src)
            writer = PdfWriter()

            for page in reader.pages:
                w = float(page.mediabox.width)
                h = float(page.mediabox.height)
                wm = (self._make_text_watermark(w, h)
                      if self.mode_var.get() == "text"
                      else self._make_image_watermark(w, h))
                page.merge_page(wm)
                writer.add_page(page)

            if not out.lower().endswith(".pdf"):
                out += ".pdf"
                self.out_var.set(out)

            with open(out, "wb") as fh:
                writer.write(fh)

            n = len(reader.pages)
            self._set_status(f"✓ Watermark applied to {n} page(s)  —  {os.path.basename(out)}")
            self.open_btn.pack(side="left", padx=8)

        except Exception as e:
            self._set_status(f"Error: {e}", ok=False)
            self.open_btn.pack_forget()
