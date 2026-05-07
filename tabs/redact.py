import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, filedialog

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.colors import black
import io

from config import BG, PANEL, ACCENT, ACCENT2, TEXT, SUBTEXT, DANGER, SUCCESS, BORDER, DROP_BG


class RedactTab:
    """Tab — Black out sensitive regions on PDF pages."""

    LABEL = "⬛  Redact PDF"

    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text=self.LABEL)
        self._regions = []   # list of (page, x_mm, y_mm, w_mm, h_mm)
        self._total   = 0
        self._build()

    def _build(self):
        f = self.frame

        tk.Label(f, text="Black out sensitive areas — add one or more regions per page",
                 bg=BG, fg=TEXT, font=("Segoe UI", 10, "bold")
                 ).pack(anchor="w", padx=20, pady=(14, 8))

        # Source file
        row1 = tk.Frame(f, bg=BG)
        row1.pack(fill="x", padx=20, pady=3)
        tk.Label(row1, text="Source PDF:", bg=BG, fg=TEXT).pack(side="left")
        self.src_var = tk.StringVar()
        tk.Entry(row1, textvariable=self.src_var, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=("Segoe UI", 10),
                 width=36).pack(side="left", padx=8)
        self._btn(row1, "📂 Open", self._pick_src, color="#334155").pack(side="left")
        self.page_lbl = tk.Label(row1, text="", bg=BG, fg=SUBTEXT, font=("Segoe UI", 9))
        self.page_lbl.pack(side="left", padx=10)

        # Region input
        tk.Label(f, text="Add redaction region  (coordinates in mm from top-left corner):",
                 bg=BG, fg=TEXT, font=("Segoe UI", 10)
                 ).pack(anchor="w", padx=20, pady=(12, 4))

        inp = tk.Frame(f, bg=BG)
        inp.pack(fill="x", padx=20, pady=2)

        fields = [("Page", "page_v", 1, 4),
                  ("X", "x_v", 0.0, 6), ("Y", "y_v", 0.0, 6),
                  ("Width", "w_v", 30.0, 6), ("Height", "h_v", 8.0, 6)]
        for label, attr, default, width in fields:
            tk.Label(inp, text=label, bg=BG, fg=SUBTEXT,
                     font=("Segoe UI", 9)).pack(side="left", padx=(0, 2))
            if label == "Page":
                var = tk.IntVar(value=default)
            else:
                var = tk.DoubleVar(value=default)
            setattr(self, attr, var)
            tk.Spinbox(inp, textvariable=var,
                       from_=0 if label != "Page" else 1,
                       to=9999, increment=1.0 if label == "Page" else 0.5,
                       width=width, bg=PANEL, fg=TEXT,
                       buttonbackground=PANEL, relief="flat",
                       font=("Segoe UI", 10)).pack(side="left", padx=(0, 10))

        self._btn(inp, "+ Add Region", self._add_region).pack(side="left")

        # Region list
        list_outer = tk.Frame(f, bg=ACCENT, padx=2, pady=2)
        list_outer.pack(fill="both", expand=True, padx=20, pady=(8, 4))
        list_inner = tk.Frame(list_outer, bg=DROP_BG)
        list_inner.pack(fill="both", expand=True)

        self.hint = tk.Label(list_inner, text="No regions added yet — use the fields above",
                             bg=DROP_BG, fg=SUBTEXT, font=("Segoe UI", 10))

        sb = ttk.Scrollbar(list_inner, orient="vertical")
        self.listbox = tk.Listbox(
            list_inner, bg=DROP_BG, fg=TEXT,
            selectbackground=ACCENT, selectforeground="white",
            font=("Consolas", 9), relief="flat", bd=0,
            activestyle="none", height=5, yscrollcommand=sb.set)
        sb.config(command=self.listbox.yview)
        self.listbox.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        sb.pack(side="right", fill="y", pady=6)
        self.hint.place(relx=0.5, rely=0.5, anchor="center")

        btn_row = tk.Frame(f, bg=BG)
        btn_row.pack(fill="x", padx=20, pady=2)
        self._btn(btn_row, "✕ Remove", self._remove_region, color=DANGER).pack(side="left", padx=(0,6))
        self._btn(btn_row, "🗑 Clear All", self._clear_regions, color="#334155").pack(side="left")

        # Output file
        out_row = tk.Frame(f, bg=BG)
        out_row.pack(fill="x", padx=20, pady=(8, 4))
        tk.Label(out_row, text="Output file:", bg=BG, fg=TEXT).pack(side="left")
        self.out_var = tk.StringVar(
            value=os.path.join(os.path.expanduser("~/Desktop"), "redacted.pdf"))
        tk.Entry(out_row, textvariable=self.out_var, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=("Segoe UI", 10),
                 width=32).pack(side="left", padx=8)
        self._btn(out_row, "📁 Save as", self._pick_out, color="#334155").pack(side="left")

        # Run
        bot = tk.Frame(f, bg=BG)
        bot.pack(fill="x", padx=20, pady=(6, 10))
        self._btn(bot, "⬛  Apply Redactions", self._run, w=20).pack(side="left")
        self.open_btn = self._btn(bot, "📂 Open folder", self._open_folder,
                                  color="#334155", w=14)
        self.open_btn.pack(side="left", padx=8)
        self.open_btn.pack_forget()
        self.status = tk.Label(bot, text="", bg=BG, font=("Segoe UI", 9))
        self.status.pack(side="left", padx=6)

    # ── Helpers ───────────────────────────────────────────────────────────────
    MM = 2.8346   # mm → points

    def _btn(self, parent, text, cmd, color=ACCENT, w=None):
        kw = dict(text=text, command=cmd, bg=color, fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat",
                  cursor="hand2", activebackground=ACCENT2,
                  activeforeground="white", pady=6, padx=12)
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

    def _pick_src(self):
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if path:
            self.src_var.set(path)
            base = os.path.splitext(os.path.basename(path))[0]
            self.out_var.set(os.path.join(os.path.dirname(path), base + "_redacted.pdf"))
            try:
                self._total = len(PdfReader(path).pages)
                self.page_lbl.config(text=f"{self._total} pages")
            except Exception:
                self._total = 0

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

    def _add_region(self):
        page = self.page_v.get()
        x, y = self.x_v.get(), self.y_v.get()
        w, h = self.w_v.get(), self.h_v.get()
        if w <= 0 or h <= 0:
            self._set_status("⚠ Width and Height must be > 0", ok=False)
            return
        self._regions.append((page, x, y, w, h))
        self.listbox.insert("end",
            f"  Page {page}   X:{x:.1f}  Y:{y:.1f}  W:{w:.1f}  H:{h:.1f}  mm")
        self._hint_update()
        self._set_status(f"Region added — {len(self._regions)} total")

    def _remove_region(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        i = sel[0]
        self._regions.pop(i)
        self.listbox.delete(i)
        self._hint_update()

    def _clear_regions(self):
        self._regions.clear()
        self.listbox.delete(0, "end")
        self._hint_update()

    # ── Run ───────────────────────────────────────────────────────────────────
    def _run(self):
        src = self.src_var.get().strip()
        out = self.out_var.get().strip()
        if not src:
            self._set_status("⚠ Please select a source PDF!", ok=False)
            return
        if not self._regions:
            self._set_status("⚠ Add at least one region!", ok=False)
            return
        try:
            reader = PdfReader(src)
            writer = PdfWriter()

            for page_idx, page in enumerate(reader.pages):
                page_num = page_idx + 1
                pw = float(page.mediabox.width)
                ph = float(page.mediabox.height)

                # Collect regions for this page
                page_regions = [(x, y, w, h)
                                for (pg, x, y, w, h) in self._regions
                                if pg == page_num]

                if page_regions:
                    buf = io.BytesIO()
                    c   = rl_canvas.Canvas(buf, pagesize=(pw, ph))
                    c.setFillColor(black)
                    for (x_mm, y_mm, w_mm, h_mm) in page_regions:
                        x_pt = x_mm * self.MM
                        w_pt = w_mm * self.MM
                        h_pt = h_mm * self.MM
                        # PDF origin is bottom-left; y_mm is from top
                        y_pt = ph - (y_mm * self.MM) - h_pt
                        c.rect(x_pt, y_pt, w_pt, h_pt, fill=1, stroke=0)
                    c.save()
                    buf.seek(0)
                    overlay = PdfReader(buf).pages[0]
                    page.merge_page(overlay)

                writer.add_page(page)

            if not out.lower().endswith(".pdf"):
                out += ".pdf"
                self.out_var.set(out)
            with open(out, "wb") as fh:
                writer.write(fh)

            n = sum(1 for (pg, *_) in self._regions
                    if any(pg == i + 1 for i in range(len(reader.pages))))
            self._set_status(
                f"✓ {len(self._regions)} region(s) redacted  —  {os.path.basename(out)}")
            self.open_btn.pack(side="left", padx=8)
        except Exception as e:
            self._set_status(f"Error: {e}", ok=False)
            self.open_btn.pack_forget()
