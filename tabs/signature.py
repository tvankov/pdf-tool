import io
import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, filedialog

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas as rl_canvas
from config import BG, PANEL, ACCENT, ACCENT2, TEXT, SUBTEXT, DANGER, SUCCESS


POSITIONS = {
    "Bottom Right":  "br",
    "Bottom Left":   "bl",
    "Bottom Center": "bc",
    "Top Right":     "tr",
    "Top Left":      "tl",
    "Top Center":    "tc",
}


class SignatureTab:
    """Tab — Place a signature image on selected pages of a PDF."""

    LABEL = "✍  Signature"

    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text=self.LABEL)
        self._build()

    def _build(self):
        f = self.frame

        tk.Label(f, text="Place a signature image on one or more pages of a PDF",
                 bg=BG, fg=TEXT, font=("Segoe UI", 10, "bold")
                 ).pack(anchor="w", padx=20, pady=(16, 10))

        # Source PDF
        row1 = tk.Frame(f, bg=BG)
        row1.pack(fill="x", padx=20, pady=3)
        tk.Label(row1, text="Source PDF:", bg=BG, fg=TEXT, width=16, anchor="w").pack(side="left")
        self.src_var = tk.StringVar()
        tk.Entry(row1, textvariable=self.src_var, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=("Segoe UI", 10),
                 width=34).pack(side="left", padx=8)
        self._btn(row1, "📂 Open", self._pick_src, color="#334155").pack(side="left")
        self.page_lbl = tk.Label(row1, text="", bg=BG, fg=SUBTEXT, font=("Segoe UI", 9))
        self.page_lbl.pack(side="left", padx=8)

        # Signature image
        row2 = tk.Frame(f, bg=BG)
        row2.pack(fill="x", padx=20, pady=3)
        tk.Label(row2, text="Signature image:", bg=BG, fg=TEXT, width=16, anchor="w").pack(side="left")
        self.img_var = tk.StringVar()
        tk.Entry(row2, textvariable=self.img_var, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=("Segoe UI", 10),
                 width=34).pack(side="left", padx=8)
        self._btn(row2, "📂 Open", self._pick_img, color="#334155").pack(side="left")
        tk.Label(row2, text="PNG recommended (supports transparency)",
                 bg=BG, fg=SUBTEXT, font=("Segoe UI", 8)).pack(side="left", padx=8)

        # Settings
        grid = tk.Frame(f, bg=BG)
        grid.pack(fill="x", padx=20, pady=(14, 4))

        def lbl(r, text):
            tk.Label(grid, text=text, bg=BG, fg=TEXT,
                     width=16, anchor="w").grid(row=r, column=0, pady=5, sticky="w")

        # Position
        lbl(0, "Position:")
        self.pos_var = tk.StringVar(value="Bottom Right")
        ttk.Combobox(grid, textvariable=self.pos_var, values=list(POSITIONS.keys()),
                     state="readonly", width=16).grid(row=0, column=1, pady=5, sticky="w", padx=8)

        # Width
        lbl(1, "Width (mm):")
        self.width_var = tk.DoubleVar(value=40.0)
        tk.Spinbox(grid, from_=5, to=200, increment=1.0,
                   textvariable=self.width_var, format="%.1f",
                   width=7, bg=PANEL, fg=TEXT, buttonbackground=PANEL,
                   relief="flat", font=("Segoe UI", 10)
                   ).grid(row=1, column=1, pady=5, sticky="w", padx=8)

        # Margin
        lbl(2, "Margin (mm):")
        self.margin_var = tk.DoubleVar(value=10.0)
        tk.Spinbox(grid, from_=0, to=100, increment=0.5,
                   textvariable=self.margin_var, format="%.1f",
                   width=7, bg=PANEL, fg=TEXT, buttonbackground=PANEL,
                   relief="flat", font=("Segoe UI", 10)
                   ).grid(row=2, column=1, pady=5, sticky="w", padx=8)

        # Opacity
        lbl(3, "Opacity:")
        op_frame = tk.Frame(grid, bg=BG)
        op_frame.grid(row=3, column=1, pady=5, sticky="w", padx=8)
        self.opacity_var = tk.IntVar(value=100)
        tk.Scale(op_frame, from_=10, to=100, orient="horizontal",
                 variable=self.opacity_var, bg=BG, fg=TEXT,
                 troughcolor=PANEL, highlightthickness=0,
                 length=160).pack(side="left")
        tk.Label(op_frame, text="%", bg=BG, fg=SUBTEXT, font=("Segoe UI", 9)).pack(side="left")

        # Pages
        lbl(4, "Apply to:")
        self.pages_mode = tk.StringVar(value="last")
        pages_frame = tk.Frame(grid, bg=BG)
        pages_frame.grid(row=4, column=1, pady=5, sticky="w", padx=8)
        for txt, val in [("Last page", "last"), ("All pages", "all"), ("Specific:", "custom")]:
            tk.Radiobutton(pages_frame, text=txt, variable=self.pages_mode, value=val,
                           bg=BG, fg=TEXT, selectcolor=ACCENT, activebackground=BG,
                           font=("Segoe UI", 10)).pack(side="left", padx=(0, 10))
        self.custom_pages = tk.StringVar(value="1")
        tk.Entry(pages_frame, textvariable=self.custom_pages, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=("Segoe UI", 10),
                 width=10).pack(side="left")
        tk.Label(pages_frame, text='e.g. "1,3,5-8"', bg=BG, fg=SUBTEXT,
                 font=("Segoe UI", 8)).pack(side="left", padx=4)

        # Output
        out_row = tk.Frame(f, bg=BG)
        out_row.pack(fill="x", padx=20, pady=(12, 4))
        tk.Label(out_row, text="Output file:", bg=BG, fg=TEXT, width=16, anchor="w").pack(side="left")
        self.out_var = tk.StringVar(
            value=os.path.join(os.path.expanduser("~/Desktop"), "signed.pdf"))
        tk.Entry(out_row, textvariable=self.out_var, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=("Segoe UI", 10),
                 width=32).pack(side="left", padx=8)
        self._btn(out_row, "📁 Save as", self._pick_out, color="#334155").pack(side="left")

        # Run
        bot = tk.Frame(f, bg=BG)
        bot.pack(fill="x", padx=20, pady=(10, 12))
        self._btn(bot, "✍  Apply Signature", self._run, w=18).pack(side="left")
        self.open_btn = self._btn(bot, "📂 Open folder", self._open_folder,
                                  color="#334155", w=14)
        self.open_btn.pack(side="left", padx=8)
        self.open_btn.pack_forget()
        self.status = tk.Label(bot, text="", bg=BG, font=("Segoe UI", 9))
        self.status.pack(side="left", padx=6)

    # ── Helpers ───────────────────────────────────────────────────────────────
    MM = 2.8346

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
            self.out_var.set(os.path.join(os.path.dirname(path), base + "_signed.pdf"))
            try:
                n = len(PdfReader(path).pages)
                self.page_lbl.config(text=f"{n} pages")
            except Exception:
                pass

    def _pick_img(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.webp"), ("All Files", "*.*")])
        if path:
            self.img_var.set(path)

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

    def _target_pages(self, total):
        mode = self.pages_mode.get()
        if mode == "last":
            return {total - 1}
        if mode == "all":
            return set(range(total))
        indices = set()
        for part in self.custom_pages.get().split(","):
            part = part.strip()
            if "-" in part:
                a, b = part.split("-", 1)
                indices.update(range(int(a) - 1, min(int(b), total)))
            elif part.isdigit():
                indices.add(int(part) - 1)
        return indices

    def _make_overlay(self, pw, ph, img_path, pos_key, w_mm, margin_mm, opacity):
        from PIL import Image as PILImage
        with PILImage.open(img_path) as img:
            iw, ih = img.size
        w_pt  = w_mm * self.MM
        h_pt  = ih * (w_pt / iw)
        m_pt  = margin_mm * self.MM
        alpha = opacity / 100

        if pos_key == "br":
            x, y = pw - w_pt - m_pt, m_pt
        elif pos_key == "bl":
            x, y = m_pt, m_pt
        elif pos_key == "bc":
            x, y = (pw - w_pt) / 2, m_pt
        elif pos_key == "tr":
            x, y = pw - w_pt - m_pt, ph - h_pt - m_pt
        elif pos_key == "tl":
            x, y = m_pt, ph - h_pt - m_pt
        else:  # tc
            x, y = (pw - w_pt) / 2, ph - h_pt - m_pt

        buf = io.BytesIO()
        c   = rl_canvas.Canvas(buf, pagesize=(pw, ph))
        c.saveState()
        c.setFillAlpha(alpha)
        c.drawImage(img_path, x, y, width=w_pt, height=h_pt, mask="auto")
        c.restoreState()
        c.save()
        buf.seek(0)
        return PdfReader(buf).pages[0]

    def _run(self):
        src = self.src_var.get().strip()
        img = self.img_var.get().strip()
        out = self.out_var.get().strip()
        if not src:
            self._set_status("⚠ Please select a source PDF!", ok=False)
            return
        if not img:
            self._set_status("⚠ Please select a signature image!", ok=False)
            return
        try:
            reader  = PdfReader(src)
            total   = len(reader.pages)
            writer  = PdfWriter()
            targets = self._target_pages(total)
            pos_key = POSITIONS[self.pos_var.get()]

            for i, page in enumerate(reader.pages):
                if i in targets:
                    pw = float(page.mediabox.width)
                    ph = float(page.mediabox.height)
                    overlay = self._make_overlay(
                        pw, ph, img, pos_key,
                        self.width_var.get(),
                        self.margin_var.get(),
                        self.opacity_var.get())
                    page.merge_page(overlay)
                writer.add_page(page)

            if not out.lower().endswith(".pdf"):
                out += ".pdf"
                self.out_var.set(out)
            with open(out, "wb") as fh:
                writer.write(fh)

            self._set_status(
                f"✓ Signature placed on {len(targets)} page(s)  —  {os.path.basename(out)}")
            self.open_btn.pack(side="left", padx=8)
        except Exception as e:
            self._set_status(f"Error: {e}", ok=False)
            self.open_btn.pack_forget()
