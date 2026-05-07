import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, filedialog

from pypdf import PdfReader, PdfWriter
from config import BG, PANEL, ACCENT, ACCENT2, TEXT, SUBTEXT, DANGER, SUCCESS


class RepairTab:
    """Tab — Attempt to repair a corrupted or broken PDF."""

    LABEL = "🔧  Repair PDF"

    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text=self.LABEL)
        self._build()

    def _build(self):
        f = self.frame

        tk.Label(f, text="Attempt to repair a corrupted or broken PDF",
                 bg=BG, fg=TEXT, font=("Segoe UI", 10, "bold")
                 ).pack(anchor="w", padx=20, pady=(16, 10))

        tk.Label(f, text=(
            "This tool re-reads the PDF page by page and rebuilds it from scratch.\n"
            "It recovers all readable pages even if some are damaged."),
                 bg=BG, fg=SUBTEXT, font=("Segoe UI", 9)
                 ).pack(anchor="w", padx=20, pady=(0, 14))

        # Source file
        row1 = tk.Frame(f, bg=BG)
        row1.pack(fill="x", padx=20, pady=4)
        tk.Label(row1, text="Source PDF:", bg=BG, fg=TEXT).pack(side="left")
        self.src_var = tk.StringVar()
        tk.Entry(row1, textvariable=self.src_var, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=("Segoe UI", 10),
                 width=38).pack(side="left", padx=8)
        self._btn(row1, "📂 Open", self._pick_src, color="#334155").pack(side="left")

        # Options
        tk.Label(f, text="Options:", bg=BG, fg=TEXT,
                 font=("Segoe UI", 10)).pack(anchor="w", padx=20, pady=(16, 6))

        self.opt_strict = tk.BooleanVar(value=False)
        tk.Checkbutton(f, text="Strict mode  —  stop on first unreadable page (off = skip bad pages)",
                       variable=self.opt_strict, bg=BG, fg=TEXT,
                       selectcolor=PANEL, activebackground=BG,
                       font=("Segoe UI", 10)).pack(anchor="w", padx=36)

        self.opt_meta = tk.BooleanVar(value=True)
        tk.Checkbutton(f, text="Copy original metadata into repaired file",
                       variable=self.opt_meta, bg=BG, fg=TEXT,
                       selectcolor=PANEL, activebackground=BG,
                       font=("Segoe UI", 10)).pack(anchor="w", padx=36, pady=(4, 0))

        # Log box
        tk.Label(f, text="Repair log:", bg=BG, fg=TEXT,
                 font=("Segoe UI", 10)).pack(anchor="w", padx=20, pady=(16, 4))
        log_frame = tk.Frame(f, bg=PANEL, padx=2, pady=2)
        log_frame.pack(fill="both", expand=True, padx=20, pady=(0, 6))
        self.log = tk.Text(log_frame, bg=PANEL, fg=TEXT, font=("Consolas", 9),
                           relief="flat", state="disabled", height=5,
                           padx=10, pady=8, wrap="word")
        self.log.pack(fill="both", expand=True)

        # Output file
        out_row = tk.Frame(f, bg=BG)
        out_row.pack(fill="x", padx=20, pady=4)
        tk.Label(out_row, text="Output file:", bg=BG, fg=TEXT).pack(side="left")
        self.out_var = tk.StringVar(
            value=os.path.join(os.path.expanduser("~/Desktop"), "repaired.pdf"))
        tk.Entry(out_row, textvariable=self.out_var, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=("Segoe UI", 10),
                 width=34).pack(side="left", padx=8)
        self._btn(out_row, "📁 Save as", self._pick_out, color="#334155").pack(side="left")

        # Run
        bot = tk.Frame(f, bg=BG)
        bot.pack(fill="x", padx=20, pady=(6, 12))
        self._btn(bot, "🔧  Repair PDF", self._run, w=16).pack(side="left")
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

    def _log(self, msg):
        self.log.config(state="normal")
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.log.config(state="disabled")

    def _clear_log(self):
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.config(state="disabled")

    def _pick_src(self):
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if path:
            self.src_var.set(path)
            base = os.path.splitext(os.path.basename(path))[0]
            self.out_var.set(os.path.join(os.path.dirname(path), base + "_repaired.pdf"))

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
        self._clear_log()
        self._log(f"Opening: {os.path.basename(src)}")
        try:
            reader = PdfReader(src, strict=self.opt_strict.get())
            total = len(reader.pages)
            self._log(f"Found {total} page(s). Rebuilding…")
            writer = PdfWriter()
            ok_pages, bad_pages = 0, []
            for i in range(total):
                try:
                    writer.add_page(reader.pages[i])
                    ok_pages += 1
                except Exception as e:
                    bad_pages.append(i + 1)
                    self._log(f"  ⚠ Page {i + 1} skipped: {e}")
            if self.opt_meta.get():
                try:
                    writer.add_metadata(reader.metadata or {})
                except Exception:
                    pass
            if not out.lower().endswith(".pdf"):
                out += ".pdf"
                self.out_var.set(out)
            with open(out, "wb") as fh:
                writer.write(fh)
            msg = f"✓ Repaired: {ok_pages}/{total} pages recovered"
            if bad_pages:
                msg += f"  —  skipped pages: {bad_pages}"
            self._log(msg)
            self._set_status(f"✓ {ok_pages}/{total} pages saved  —  {os.path.basename(out)}")
            self.open_btn.pack(side="left", padx=8)
        except Exception as e:
            self._log(f"Fatal error: {e}")
            self._set_status(f"Error: {e}", ok=False)
            self.open_btn.pack_forget()
