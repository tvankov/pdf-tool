import io
import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, filedialog

from pypdf import PdfReader, PdfWriter, PageObject, Transformation
from pypdf.generic import ArrayObject, FloatObject

from config import BG, PANEL, ACCENT, ACCENT2, TEXT, SUBTEXT, DANGER, SUCCESS


LAYOUTS = {
    "2-up (1×2 landscape)": (1, 2),
    "4-up (2×2)":           (2, 2),
    "6-up (2×3 landscape)": (2, 3),
    "9-up (3×3)":           (3, 3),
}

PAGE_SIZES = {
    "A4 Portrait  (210×297 mm)":  (595.28, 841.89),
    "A4 Landscape (297×210 mm)":  (841.89, 595.28),
    "Letter Portrait  (8.5×11\")": (612.0,  792.0),
    "Letter Landscape (11×8.5\")": (792.0,  612.0),
}


class NupTab:
    """Tab — Place multiple PDF pages per sheet (N-up imposition)."""

    LABEL = "📄⊞  N-Up"

    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text=self.LABEL)
        self._build()

    def _build(self):
        f = self.frame

        tk.Label(f, text="Print multiple pages per sheet — 2-up, 4-up, 6-up or 9-up",
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

        # Settings grid
        grid = tk.Frame(f, bg=BG)
        grid.pack(fill="x", padx=20, pady=(14, 4))

        def lbl(r, text):
            tk.Label(grid, text=text, bg=BG, fg=TEXT,
                     width=16, anchor="w").grid(row=r, column=0, pady=6, sticky="w")

        # Layout
        lbl(0, "Layout:")
        self.layout_var = tk.StringVar(value="2-up (1×2 landscape)")
        ttk.Combobox(grid, textvariable=self.layout_var, values=list(LAYOUTS.keys()),
                     state="readonly", width=26).grid(row=0, column=1, pady=6, sticky="w", padx=8)

        # Output page size
        lbl(1, "Output page size:")
        self.size_var = tk.StringVar(value="A4 Landscape (297×210 mm)")
        ttk.Combobox(grid, textvariable=self.size_var, values=list(PAGE_SIZES.keys()),
                     state="readonly", width=26).grid(row=1, column=1, pady=6, sticky="w", padx=8)

        # Order
        lbl(2, "Page order:")
        self.order_var = tk.StringVar(value="left-to-right")
        ttk.Combobox(grid, textvariable=self.order_var,
                     values=["left-to-right", "top-to-bottom"],
                     state="readonly", width=16).grid(row=2, column=1, pady=6, sticky="w", padx=8)

        # Margin between cells
        lbl(3, "Gap (mm):")
        self.gap_var = tk.DoubleVar(value=4.0)
        tk.Spinbox(grid, from_=0, to=30, increment=0.5, textvariable=self.gap_var,
                   format="%.1f", width=7, bg=PANEL, fg=TEXT,
                   buttonbackground=PANEL, relief="flat", font=("Segoe UI", 10)
                   ).grid(row=3, column=1, pady=6, sticky="w", padx=8)

        # Outer margin
        lbl(4, "Outer margin (mm):")
        self.margin_var = tk.DoubleVar(value=6.0)
        tk.Spinbox(grid, from_=0, to=50, increment=0.5, textvariable=self.margin_var,
                   format="%.1f", width=7, bg=PANEL, fg=TEXT,
                   buttonbackground=PANEL, relief="flat", font=("Segoe UI", 10)
                   ).grid(row=4, column=1, pady=6, sticky="w", padx=8)

        # Draw borders around cells
        self.border_var = tk.BooleanVar(value=False)
        tk.Checkbutton(f, text="Draw border around each cell",
                       variable=self.border_var,
                       bg=BG, fg=TEXT, selectcolor=PANEL, activebackground=BG,
                       font=("Segoe UI", 10)).pack(anchor="w", padx=20, pady=(4, 4))

        # Output file
        out_row = tk.Frame(f, bg=BG)
        out_row.pack(fill="x", padx=20, pady=(10, 4))
        tk.Label(out_row, text="Output file:", bg=BG, fg=TEXT, width=16, anchor="w").pack(side="left")
        self.out_var = tk.StringVar(
            value=os.path.join(os.path.expanduser("~/Desktop"), "nup.pdf"))
        tk.Entry(out_row, textvariable=self.out_var, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=("Segoe UI", 10),
                 width=32).pack(side="left", padx=8)
        self._btn(out_row, "📁 Save as", self._pick_out, color="#334155").pack(side="left")

        # Run
        bot = tk.Frame(f, bg=BG)
        bot.pack(fill="x", padx=20, pady=(10, 12))
        self._btn(bot, "📄⊞  Create N-Up PDF", self._run).pack(side="left")
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
            self.out_var.set(os.path.join(os.path.dirname(path), base + "_nup.pdf"))
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

    def _run(self):
        src = self.src_var.get().strip()
        out = self.out_var.get().strip()
        if not src:
            self._set_status("⚠ Please select a source PDF!", ok=False)
            return
        try:
            reader   = PdfReader(src)
            pages    = reader.pages
            n_pages  = len(pages)

            rows, cols = LAYOUTS[self.layout_var.get()]
            per_sheet  = rows * cols
            out_w, out_h = PAGE_SIZES[self.size_var.get()]
            gap    = self.gap_var.get() * self.MM
            margin = self.margin_var.get() * self.MM
            draw_border = self.border_var.get()
            order  = self.order_var.get()

            # Available area per cell
            avail_w = (out_w - 2 * margin - (cols - 1) * gap) / cols
            avail_h = (out_h - 2 * margin - (rows - 1) * gap) / rows

            writer = PdfWriter()

            # Chunk source pages into sheets
            for sheet_start in range(0, n_pages, per_sheet):
                chunk = pages[sheet_start: sheet_start + per_sheet]

                # Create a blank output page
                out_page = PageObject.create_blank_page(width=out_w, height=out_h)

                for slot, src_page in enumerate(chunk):
                    if order == "left-to-right":
                        r, c = divmod(slot, cols)
                    else:
                        c, r = divmod(slot, rows)

                    # Top-left origin of this cell (PDF y goes up)
                    cell_x = margin + c * (avail_w + gap)
                    cell_y = out_h - margin - (r + 1) * avail_h - r * gap

                    src_w = float(src_page.mediabox.width)
                    src_h = float(src_page.mediabox.height)
                    scale = min(avail_w / src_w, avail_h / src_h)

                    # Center within cell
                    placed_w = src_w * scale
                    placed_h = src_h * scale
                    x_off = cell_x + (avail_w - placed_w) / 2
                    y_off = cell_y + (avail_h - placed_h) / 2

                    t = Transformation().scale(scale).translate(x_off, y_off)
                    src_page.add_transformation(t)
                    src_page.mediabox.lower_left  = (x_off, y_off)
                    src_page.mediabox.upper_right = (x_off + placed_w, y_off + placed_h)
                    out_page.merge_page(src_page)

                if draw_border:
                    self._draw_borders(out_page, out_w, out_h,
                                       rows, cols, margin, gap, avail_w, avail_h)

                writer.add_page(out_page)

            if not out.lower().endswith(".pdf"):
                out += ".pdf"
                self.out_var.set(out)
            with open(out, "wb") as fh:
                writer.write(fh)

            out_pages = -(-n_pages // per_sheet)  # ceiling div
            self._set_status(
                f"✓ {n_pages} pages → {out_pages} sheet(s)  —  {os.path.basename(out)}")
            self.open_btn.pack(side="left", padx=8)
        except Exception as e:
            self._set_status(f"Error: {e}", ok=False)
            self.open_btn.pack_forget()

    def _draw_borders(self, page, out_w, out_h, rows, cols, margin, gap, avail_w, avail_h):
        """Overlay thin gray rectangles around each cell using reportlab."""
        from reportlab.pdfgen import canvas as rl_canvas
        from reportlab.lib.colors import gray
        buf = io.BytesIO()
        c = rl_canvas.Canvas(buf, pagesize=(out_w, out_h))
        c.setStrokeColor(gray)
        c.setLineWidth(0.5)
        for r in range(rows):
            for col in range(cols):
                x = margin + col * (avail_w + gap)
                y = out_h - margin - (r + 1) * avail_h - r * gap
                c.rect(x, y, avail_w, avail_h, fill=0, stroke=1)
        c.save()
        buf.seek(0)
        overlay = PdfReader(buf).pages[0]
        page.merge_page(overlay)
