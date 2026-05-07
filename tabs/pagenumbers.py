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


POSITIONS = {
    "Bottom Center":  "bc",
    "Bottom Left":    "bl",
    "Bottom Right":   "br",
    "Top Center":     "tc",
    "Top Left":       "tl",
    "Top Right":      "tr",
}

FORMATS = [
    "1",
    "Page 1",
    "1 / {total}",
    "Page 1 of {total}",
    "- 1 -",
]

COLORS = {
    "Black": (0.0, 0.0, 0.0),
    "Gray":  (0.5, 0.5, 0.5),
    "White": (1.0, 1.0, 1.0),
}


class PageNumbersTab:
    """Tab — Add page numbers to every page of a PDF."""

    LABEL = "🔢  Page Numbers"

    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text=self.LABEL)
        self._build()

    def _build(self):
        f = self.frame

        tk.Label(f, text="Add page numbers to a PDF — choose position, format and style",
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
        self.page_lbl = tk.Label(row1, text="", bg=BG, fg=SUBTEXT, font=("Segoe UI", 9))
        self.page_lbl.pack(side="left", padx=10)

        # Settings grid
        grid = tk.Frame(f, bg=BG)
        grid.pack(fill="x", padx=20, pady=(14, 4))

        def row(parent, label, widget_fn, r):
            tk.Label(parent, text=label, bg=BG, fg=TEXT,
                     width=16, anchor="w").grid(row=r, column=0, pady=5, sticky="w")
            w = widget_fn(parent)
            w.grid(row=r, column=1, pady=5, sticky="w", padx=8)

        # Position
        self.pos_var = tk.StringVar(value="Bottom Center")
        row(grid, "Position:", lambda p: ttk.Combobox(
            p, textvariable=self.pos_var, values=list(POSITIONS.keys()),
            state="readonly", width=18), 0)

        # Format
        self.fmt_var = tk.StringVar(value="1 / {total}")
        row(grid, "Format:", lambda p: ttk.Combobox(
            p, textvariable=self.fmt_var, values=FORMATS,
            state="normal", width=18), 1)

        # Start number
        self.start_var = tk.IntVar(value=1)
        row(grid, "Start number:", lambda p: tk.Spinbox(
            p, from_=0, to=9999, textvariable=self.start_var,
            width=6, bg=PANEL, fg=TEXT, buttonbackground=PANEL,
            relief="flat", font=("Segoe UI", 10)), 2)

        # Font size
        self.size_var = tk.IntVar(value=10)
        row(grid, "Font size:", lambda p: tk.Spinbox(
            p, from_=6, to=72, textvariable=self.size_var,
            width=6, bg=PANEL, fg=TEXT, buttonbackground=PANEL,
            relief="flat", font=("Segoe UI", 10)), 3)

        # Color
        self.color_var = tk.StringVar(value="Black")
        row(grid, "Color:", lambda p: ttk.Combobox(
            p, textvariable=self.color_var, values=list(COLORS.keys()),
            state="readonly", width=10), 4)

        # Margin
        self.margin_var = tk.DoubleVar(value=10.0)
        row(grid, "Margin (mm):", lambda p: tk.Spinbox(
            p, from_=2, to=50, increment=0.5,
            textvariable=self.margin_var, format="%.1f",
            width=6, bg=PANEL, fg=TEXT, buttonbackground=PANEL,
            relief="flat", font=("Segoe UI", 10)), 5)

        # Skip first page option
        self.skip_first = tk.BooleanVar(value=False)
        tk.Checkbutton(f, text="Skip first page (e.g. cover page)",
                       variable=self.skip_first,
                       bg=BG, fg=TEXT, selectcolor=PANEL, activebackground=BG,
                       font=("Segoe UI", 10)).pack(anchor="w", padx=20, pady=(4, 4))

        # Output file
        out_row = tk.Frame(f, bg=BG)
        out_row.pack(fill="x", padx=20, pady=(10, 4))
        tk.Label(out_row, text="Output file:", bg=BG, fg=TEXT).pack(side="left")
        self.out_var = tk.StringVar(
            value=os.path.join(os.path.expanduser("~/Desktop"), "numbered.pdf"))
        tk.Entry(out_row, textvariable=self.out_var, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=("Segoe UI", 10),
                 width=32).pack(side="left", padx=8)
        self._btn(out_row, "📁 Save as", self._pick_out, color="#334155").pack(side="left")

        # Run
        bot = tk.Frame(f, bg=BG)
        bot.pack(fill="x", padx=20, pady=(10, 12))
        self._btn(bot, "🔢  Add Page Numbers", self._run, w=20).pack(side="left")
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
            self.out_var.set(os.path.join(os.path.dirname(path), base + "_numbered.pdf"))
            try:
                n = len(PdfReader(path).pages)
                self.page_lbl.config(text=f"{n} pages")
            except Exception:
                pass

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

    def _make_number_overlay(self, pw, ph, label, pos_key, font_size, color_rgb, margin_pt):
        buf = io.BytesIO()
        c   = rl_canvas.Canvas(buf, pagesize=(pw, ph))
        r, g, b = color_rgb
        c.setFillColor(RLColor(r, g, b))
        c.setFont("Helvetica", font_size)
        m = margin_pt

        if pos_key == "bc":
            c.drawCentredString(pw / 2, m, label)
        elif pos_key == "bl":
            c.drawString(m, m, label)
        elif pos_key == "br":
            c.drawRightString(pw - m, m, label)
        elif pos_key == "tc":
            c.drawCentredString(pw / 2, ph - m - font_size, label)
        elif pos_key == "tl":
            c.drawString(m, ph - m - font_size, label)
        elif pos_key == "tr":
            c.drawRightString(pw - m, ph - m - font_size, label)

        c.save()
        buf.seek(0)
        return PdfReader(buf).pages[0]

    def _run(self):
        src = self.src_var.get().strip()
        out = self.out_var.get().strip()
        if not src:
            self._set_status("⚠ Please select a source PDF!", ok=False)
            return
        try:
            reader    = PdfReader(src)
            total     = len(reader.pages)
            writer    = PdfWriter()
            pos_key   = POSITIONS[self.pos_var.get()]
            fmt       = self.fmt_var.get()
            start     = self.start_var.get()
            font_size = self.size_var.get()
            color_rgb = COLORS[self.color_var.get()]
            margin_pt = self.margin_var.get() * self.MM
            skip      = self.skip_first.get()

            for i, page in enumerate(reader.pages):
                if skip and i == 0:
                    writer.add_page(page)
                    continue

                display_num = start + i - (1 if skip else 0)
                label = fmt.replace("{total}", str(total)).replace("1", str(display_num), 1)

                pw = float(page.mediabox.width)
                ph = float(page.mediabox.height)
                overlay = self._make_number_overlay(
                    pw, ph, label, pos_key, font_size, color_rgb, margin_pt)
                page.merge_page(overlay)
                writer.add_page(page)

            if not out.lower().endswith(".pdf"):
                out += ".pdf"
                self.out_var.set(out)
            with open(out, "wb") as fh:
                writer.write(fh)

            self._set_status(f"✓ Page numbers added to {total} pages  —  {os.path.basename(out)}")
            self.open_btn.pack(side="left", padx=8)
        except Exception as e:
            self._set_status(f"Error: {e}", ok=False)
            self.open_btn.pack_forget()
