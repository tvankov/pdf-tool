import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, filedialog

from pypdf import PdfReader, PdfWriter
from config import BG, PANEL, ACCENT, ACCENT2, TEXT, SUBTEXT, DANGER, SUCCESS


class RotateTab:
    """Tab — Rotate pages of a PDF by 90, 180 or 270 degrees."""

    LABEL = "🔄  Rotate"

    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text=self.LABEL)
        self._build()

    def _build(self):
        f = self.frame

        tk.Label(f, text="Rotate PDF pages — all, a range, or specific page numbers",
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

        self.page_count_label = tk.Label(f, text="", bg=BG, fg=SUBTEXT, font=("Segoe UI", 9))
        self.page_count_label.pack(anchor="w", padx=20, pady=(2, 0))

        # Pages selection
        tk.Label(f, text="Pages:", bg=BG, fg=TEXT,
                 font=("Segoe UI", 10)).pack(anchor="w", padx=20, pady=(14, 4))

        self.mode_var = tk.StringVar(value="all")
        tk.Radiobutton(f, text="All pages", variable=self.mode_var, value="all",
                       bg=BG, fg=TEXT, selectcolor=ACCENT, activebackground=BG,
                       font=("Segoe UI", 10), command=self._on_mode).pack(anchor="w", padx=36)
        tk.Radiobutton(f, text="Page range", variable=self.mode_var, value="range",
                       bg=BG, fg=TEXT, selectcolor=ACCENT, activebackground=BG,
                       font=("Segoe UI", 10), command=self._on_mode).pack(anchor="w", padx=36)
        tk.Radiobutton(f, text="Specific pages", variable=self.mode_var, value="specific",
                       bg=BG, fg=TEXT, selectcolor=ACCENT, activebackground=BG,
                       font=("Segoe UI", 10), command=self._on_mode).pack(anchor="w", padx=36)

        # Range row
        self.range_row = tk.Frame(f, bg=BG)
        self.range_row.pack(fill="x", padx=20, pady=(4, 0))
        tk.Label(self.range_row, text="From:", bg=BG, fg=TEXT).pack(side="left", padx=(36, 0))
        self.from_var = tk.IntVar(value=1)
        tk.Spinbox(self.range_row, from_=1, to=9999, textvariable=self.from_var,
                   width=5, bg=PANEL, fg=TEXT, buttonbackground=PANEL,
                   relief="flat", font=("Segoe UI", 10)).pack(side="left", padx=6)
        tk.Label(self.range_row, text="To:", bg=BG, fg=TEXT).pack(side="left", padx=(10, 0))
        self.to_var = tk.IntVar(value=1)
        tk.Spinbox(self.range_row, from_=1, to=9999, textvariable=self.to_var,
                   width=5, bg=PANEL, fg=TEXT, buttonbackground=PANEL,
                   relief="flat", font=("Segoe UI", 10)).pack(side="left", padx=6)

        # Specific pages row
        self.specific_row = tk.Frame(f, bg=BG)
        self.specific_row.pack(fill="x", padx=20, pady=(4, 0))
        tk.Label(self.specific_row, text="Pages:", bg=BG, fg=TEXT).pack(side="left", padx=(36, 0))
        self.pages_var = tk.StringVar()
        tk.Entry(self.specific_row, textvariable=self.pages_var, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=("Segoe UI", 10),
                 width=24).pack(side="left", padx=8)
        tk.Label(self.specific_row, text='e.g.  "1, 3, 5-8"', bg=BG, fg=SUBTEXT,
                 font=("Segoe UI", 9)).pack(side="left")

        self._on_mode()

        # Rotation buttons
        tk.Label(f, text="Rotation:", bg=BG, fg=TEXT,
                 font=("Segoe UI", 10)).pack(anchor="w", padx=20, pady=(16, 6))

        self.angle_var = tk.IntVar(value=90)
        rot_row = tk.Frame(f, bg=BG)
        rot_row.pack(anchor="w", padx=36)
        for label, val in [("↻  90° clockwise", 90),
                           ("↕  180°",          180),
                           ("↺  90° counter-clockwise", 270)]:
            tk.Radiobutton(rot_row, text=label, variable=self.angle_var, value=val,
                           bg=BG, fg=TEXT, selectcolor=ACCENT, activebackground=BG,
                           font=("Segoe UI", 10)).pack(side="left", padx=(0, 20))

        # Output file
        out_row = tk.Frame(f, bg=BG)
        out_row.pack(fill="x", padx=20, pady=(16, 4))
        tk.Label(out_row, text="Output file:", bg=BG, fg=TEXT).pack(side="left")
        self.out_var = tk.StringVar(
            value=os.path.join(os.path.expanduser("~/Desktop"), "rotated.pdf"))
        tk.Entry(out_row, textvariable=self.out_var, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=("Segoe UI", 10),
                 width=34).pack(side="left", padx=8)
        self._btn(out_row, "📁 Save as", self._pick_out, color="#334155").pack(side="left")

        # Run
        bot = tk.Frame(f, bg=BG)
        bot.pack(fill="x", padx=20, pady=(12, 12))
        self._btn(bot, "🔄  Rotate", self._run, w=14).pack(side="left")
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

    def _on_mode(self):
        mode = self.mode_var.get()
        for w in self.range_row.winfo_children():
            w.config(state="normal" if mode == "range" else "disabled")
        for w in self.specific_row.winfo_children():
            w.config(state="normal" if mode == "specific" else "disabled")

    def _pick_src(self):
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if path:
            self.src_var.set(path)
            base = os.path.splitext(os.path.basename(path))[0]
            self.out_var.set(os.path.join(os.path.dirname(path), base + "_rotated.pdf"))
            try:
                total = len(PdfReader(path).pages)
                self.page_count_label.config(text=f"{total} page(s)")
                self.to_var.set(total)
            except Exception:
                self.page_count_label.config(text="")

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

    def _parse_pages(self, total):
        """Parse specific pages string like '1, 3, 5-8' into a set of 0-based indices."""
        indices = set()
        for part in self.pages_var.get().split(","):
            part = part.strip()
            if "-" in part:
                a, b = part.split("-", 1)
                indices.update(range(int(a) - 1, min(int(b), total)))
            elif part.isdigit():
                indices.add(int(part) - 1)
        return indices

    # ── Actions ───────────────────────────────────────────────────────────────
    def _run(self):
        src   = self.src_var.get().strip()
        out   = self.out_var.get().strip()
        angle = self.angle_var.get()

        if not src:
            self._set_status("⚠ Please select a source PDF!", ok=False)
            return

        try:
            reader = PdfReader(src)
            total  = len(reader.pages)
            writer = PdfWriter()

            mode = self.mode_var.get()
            if mode == "all":
                rotate_indices = set(range(total))
            elif mode == "range":
                rotate_indices = set(range(
                    max(0, self.from_var.get() - 1),
                    min(total, self.to_var.get())))
            else:
                rotate_indices = self._parse_pages(total)
                if not rotate_indices:
                    self._set_status("⚠ No valid page numbers entered!", ok=False)
                    return

            for i, page in enumerate(reader.pages):
                if i in rotate_indices:
                    page.rotate(angle)
                writer.add_page(page)

            if not out.lower().endswith(".pdf"):
                out += ".pdf"
                self.out_var.set(out)

            with open(out, "wb") as fh:
                writer.write(fh)

            label = {90: "90° clockwise", 180: "180°", 270: "90° counter-clockwise"}[angle]
            self._set_status(
                f"✓ {len(rotate_indices)} page(s) rotated {label}  —  {os.path.basename(out)}")
            self.open_btn.pack(side="left", padx=8)

        except Exception as e:
            self._set_status(f"Error: {e}", ok=False)
            self.open_btn.pack_forget()
