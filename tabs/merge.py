import os
import re
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, filedialog

from pypdf import PdfWriter
from config import (BG, PANEL, ACCENT, ACCENT2, TEXT, SUBTEXT,
                    DANGER, SUCCESS, BORDER, DROP_BG)

try:
    from tkinterdnd2 import DND_FILES
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False


class MergeTab:
    """Tab 1 — Merge multiple PDFs into one file."""

    LABEL = "  ➕  Merge PDFs  "

    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text=self.LABEL)
        self._build()

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build(self):
        f = self.frame

        tk.Label(f, text="Files  —  drag & drop PDFs or use the buttons below",
                 bg=BG, fg=TEXT, font=("Segoe UI", 10, "bold")
                 ).pack(anchor="w", padx=20, pady=(16, 6))

        # Drop zone
        drop_outer = tk.Frame(f, bg=ACCENT, padx=2, pady=2)
        drop_outer.pack(fill="both", expand=True, padx=20, pady=(0, 4))
        drop_inner = tk.Frame(drop_outer, bg=DROP_BG)
        drop_inner.pack(fill="both", expand=True)

        self.hint = tk.Label(drop_inner, text="⬇   Drop PDF files here",
                             bg=DROP_BG, fg=SUBTEXT, font=("Segoe UI", 12))

        sb = ttk.Scrollbar(drop_inner, orient="vertical")
        self.listbox = tk.Listbox(
            drop_inner, bg=DROP_BG, fg=TEXT,
            selectbackground=ACCENT, selectforeground="white",
            font=("Segoe UI", 10), relief="flat", bd=0,
            activestyle="none", height=7, yscrollcommand=sb.set)
        sb.config(command=self.listbox.yview)
        self.listbox.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        sb.pack(side="right", fill="y", pady=6)
        self.hint.place(relx=0.5, rely=0.5, anchor="center")

        if DND_AVAILABLE:
            for widget in (drop_inner, self.listbox, self.hint):
                widget.drop_target_register(DND_FILES)
                widget.dnd_bind("<<Drop>>", self._on_drop)

        # Buttons
        row = tk.Frame(f, bg=BG)
        row.pack(fill="x", padx=20, pady=6)
        self._btn(row, "+ Add Files",  self._add).pack(side="left", padx=(0, 6))
        self._btn(row, "↑ Up",         self._up,     color="#334155").pack(side="left", padx=(0, 6))
        self._btn(row, "↓ Down",       self._down,   color="#334155").pack(side="left", padx=(0, 6))
        self._btn(row, "✕ Remove",     self._remove, color=DANGER).pack(side="left", padx=(0, 6))
        self._btn(row, "🗑 Clear All",  self._clear,  color="#334155").pack(side="left")

        # Output path
        out_row = tk.Frame(f, bg=BG)
        out_row.pack(fill="x", padx=20, pady=(2, 6))
        tk.Label(out_row, text="Output file:", bg=BG, fg=TEXT).pack(side="left")
        self.out_var = tk.StringVar(
            value=os.path.join(os.path.expanduser("~/Desktop"), "merged.pdf"))
        tk.Entry(out_row, textvariable=self.out_var, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=("Segoe UI", 10),
                 width=32).pack(side="left", padx=8)
        self._btn(out_row, "📁 Save as", self._pick_out, color="#334155").pack(side="left")

        # Run row
        bot = tk.Frame(f, bg=BG)
        bot.pack(fill="x", padx=20, pady=(0, 12))
        self._btn(bot, "🔗  Merge PDFs", self._run, w=20).pack(side="left")
        self.open_btn = self._btn(bot, "📂 Open folder", self._open_folder,
                                  color="#334155", w=14)
        self.open_btn.pack(side="left", padx=8)
        self.open_btn.pack_forget()
        self.status = tk.Label(bot, text="", bg=BG, font=("Segoe UI", 9))
        self.status.pack(side="left", padx=6)

        if not DND_AVAILABLE:
            tk.Label(f, bg=BG, fg=SUBTEXT, font=("Segoe UI", 8),
                     text="ℹ  For drag & drop install:  pip install tkinterdnd2"
                     ).pack(anchor="w", padx=22, pady=(0, 4))

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
        self.hint.lift() if self.listbox.size() == 0 else self.hint.lower()

    # ── Actions ───────────────────────────────────────────────────────────────
    def _on_drop(self, event):
        paths = re.findall(r'\{([^}]+)\}', event.data)
        plain = re.sub(r'\{[^}]+\}', '', event.data).strip()
        if plain:
            paths += plain.split()
        added = sum(1 for p in paths
                    if p.strip().lower().endswith(".pdf")
                    and os.path.isfile(p.strip())
                    and not self.listbox.insert("end", p.strip()) or True)
        self._set_status(f"✓ {added} file(s) added" if added else "⚠ No valid PDFs dropped",
                         ok=bool(added))
        self._hint_update()

    def _add(self):
        for p in filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")]):
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
            initialfile="merged.pdf",
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

    def _run(self):
        files = list(self.listbox.get(0, "end"))
        if len(files) < 2:
            self._set_status("⚠ Select at least 2 files!", ok=False)
            self.open_btn.pack_forget()
            return
        out = self.out_var.get().strip()
        if not out.lower().endswith(".pdf"):
            out += ".pdf"
            self.out_var.set(out)
        out_dir = os.path.dirname(os.path.abspath(out))
        if not os.path.isdir(out_dir):
            self._set_status(f"⚠ Folder not found: {out_dir}", ok=False)
            return
        try:
            writer = PdfWriter()
            for f in files:
                writer.append(f)
            abs_out = os.path.abspath(out)
            with open(abs_out, "wb") as fh:
                writer.write(fh)
            self.out_var.set(abs_out)
            self._set_status(f"✓ Saved: {os.path.basename(abs_out)}")
            self.open_btn.pack(side="left", padx=8)
        except Exception as e:
            self._set_status(f"Error: {e}", ok=False)
            self.open_btn.pack_forget()
