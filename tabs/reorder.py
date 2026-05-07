import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, filedialog

from pypdf import PdfReader, PdfWriter
from config import BG, PANEL, ACCENT, ACCENT2, TEXT, SUBTEXT, DANGER, SUCCESS, DROP_BG


class ReorderTab:
    """Tab — Reorder, duplicate, or delete pages of a PDF."""

    LABEL = "↕  Reorder"

    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text=self.LABEL)
        self._page_order = []   # list of original 0-based page indices
        self._total      = 0
        self._build()

    def _build(self):
        f = self.frame

        tk.Label(f, text="Reorder, delete, or duplicate pages — then save a new PDF",
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

        # Page list
        list_outer = tk.Frame(f, bg=ACCENT, padx=2, pady=2)
        list_outer.pack(fill="both", expand=True, padx=20, pady=(8, 4))
        list_inner = tk.Frame(list_outer, bg=DROP_BG)
        list_inner.pack(fill="both", expand=True)

        self.hint = tk.Label(list_inner, text="Open a PDF to see its pages here",
                             bg=DROP_BG, fg=SUBTEXT, font=("Segoe UI", 11))

        sb = ttk.Scrollbar(list_inner, orient="vertical")
        self.listbox = tk.Listbox(
            list_inner, bg=DROP_BG, fg=TEXT,
            selectbackground=ACCENT, selectforeground="white",
            font=("Segoe UI", 10), relief="flat", bd=0,
            activestyle="none", height=7, yscrollcommand=sb.set)
        sb.config(command=self.listbox.yview)
        self.listbox.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        sb.pack(side="right", fill="y", pady=6)
        self.hint.place(relx=0.5, rely=0.5, anchor="center")

        # Action buttons
        btn_row = tk.Frame(f, bg=BG)
        btn_row.pack(fill="x", padx=20, pady=4)
        self._btn(btn_row, "↑ Up",         self._up,        color="#334155").pack(side="left", padx=(0, 6))
        self._btn(btn_row, "↓ Down",       self._down,      color="#334155").pack(side="left", padx=(0, 6))
        self._btn(btn_row, "⧉ Duplicate",  self._duplicate, color="#334155").pack(side="left", padx=(0, 6))
        self._btn(btn_row, "✕ Delete",     self._delete,    color=DANGER   ).pack(side="left", padx=(0, 6))
        self._btn(btn_row, "↺ Reset",      self._reset,     color="#334155").pack(side="left")

        self.page_info = tk.Label(f, text="", bg=BG, fg=SUBTEXT, font=("Segoe UI", 9))
        self.page_info.pack(anchor="w", padx=22)

        # Output file
        out_row = tk.Frame(f, bg=BG)
        out_row.pack(fill="x", padx=20, pady=(6, 4))
        tk.Label(out_row, text="Output file:", bg=BG, fg=TEXT).pack(side="left")
        self.out_var = tk.StringVar(
            value=os.path.join(os.path.expanduser("~/Desktop"), "reordered.pdf"))
        tk.Entry(out_row, textvariable=self.out_var, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=("Segoe UI", 10),
                 width=34).pack(side="left", padx=8)
        self._btn(out_row, "📁 Save as", self._pick_out, color="#334155").pack(side="left")

        # Run
        bot = tk.Frame(f, bg=BG)
        bot.pack(fill="x", padx=20, pady=(6, 12))
        self._btn(bot, "💾  Save PDF", self._run, w=16).pack(side="left")
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

    def _hint_update(self):
        if self.listbox.size() == 0:
            self.hint.lift()
        else:
            self.hint.lower()

    def _refresh_list(self):
        self.listbox.delete(0, "end")
        for pos, orig in enumerate(self._page_order):
            marker = f"  (copy of p.{orig + 1})" if self._page_order.count(orig) > 1 else ""
            self.listbox.insert("end", f"  Page {orig + 1}{marker}")
        self._hint_update()
        n = self.listbox.size()
        self.page_info.config(
            text=f"{n} page(s)  —  original: {self._total}")

    def _pick_src(self):
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if path:
            self.src_var.set(path)
            base = os.path.splitext(os.path.basename(path))[0]
            self.out_var.set(os.path.join(os.path.dirname(path), base + "_reordered.pdf"))
            try:
                self._total      = len(PdfReader(path).pages)
                self._page_order = list(range(self._total))
                self._refresh_list()
            except Exception as e:
                self._set_status(f"Error reading PDF: {e}", ok=False)

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

    # ── List actions ──────────────────────────────────────────────────────────
    def _up(self):
        sel = self.listbox.curselection()
        if not sel or sel[0] == 0:
            return
        i = sel[0]
        self._page_order[i - 1], self._page_order[i] = self._page_order[i], self._page_order[i - 1]
        self._refresh_list()
        self.listbox.select_set(i - 1)
        self.listbox.see(i - 1)

    def _down(self):
        sel = self.listbox.curselection()
        if not sel or sel[0] == self.listbox.size() - 1:
            return
        i = sel[0]
        self._page_order[i], self._page_order[i + 1] = self._page_order[i + 1], self._page_order[i]
        self._refresh_list()
        self.listbox.select_set(i + 1)
        self.listbox.see(i + 1)

    def _duplicate(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        i = sel[0]
        self._page_order.insert(i + 1, self._page_order[i])
        self._refresh_list()
        self.listbox.select_set(i + 1)

    def _delete(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        if len(self._page_order) <= 1:
            self._set_status("⚠ Cannot delete the last page!", ok=False)
            return
        i = sel[0]
        self._page_order.pop(i)
        self._refresh_list()
        self.listbox.select_set(min(i, self.listbox.size() - 1))

    def _reset(self):
        if self._total:
            self._page_order = list(range(self._total))
            self._refresh_list()

    # ── Save ──────────────────────────────────────────────────────────────────
    def _run(self):
        src = self.src_var.get().strip()
        out = self.out_var.get().strip()

        if not src:
            self._set_status("⚠ Please select a source PDF!", ok=False)
            return
        if not self._page_order:
            self._set_status("⚠ No pages in the list!", ok=False)
            return

        try:
            reader = PdfReader(src)
            writer = PdfWriter()
            for idx in self._page_order:
                writer.add_page(reader.pages[idx])

            if not out.lower().endswith(".pdf"):
                out += ".pdf"
                self.out_var.set(out)

            with open(out, "wb") as fh:
                writer.write(fh)

            self._set_status(
                f"✓ Saved {len(self._page_order)} page(s)  —  {os.path.basename(out)}")
            self.open_btn.pack(side="left", padx=8)

        except Exception as e:
            self._set_status(f"Error: {e}", ok=False)
            self.open_btn.pack_forget()
