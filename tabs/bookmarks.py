import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog

from pypdf import PdfReader, PdfWriter

from config import BG, PANEL, ACCENT, ACCENT2, TEXT, SUBTEXT, DANGER, SUCCESS, BORDER, DROP_BG


class BookmarksTab:
    """Tab — View, add, delete PDF bookmarks; split a PDF by bookmark."""

    LABEL = "🔖  Bookmarks"

    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text=self.LABEL)
        self._reader   = None
        self._src_path = ""
        self._flat     = []   # list of (indent, title, page_num)
        self._build()

    def _build(self):
        f = self.frame

        tk.Label(f, text="View, add or delete bookmarks — or split a PDF by bookmark",
                 bg=BG, fg=TEXT, font=("Segoe UI", 10, "bold")
                 ).pack(anchor="w", padx=20, pady=(14, 8))

        # Source file
        row1 = tk.Frame(f, bg=BG)
        row1.pack(fill="x", padx=20, pady=3)
        tk.Label(row1, text="Source PDF:", bg=BG, fg=TEXT, width=14, anchor="w").pack(side="left")
        self.src_var = tk.StringVar()
        tk.Entry(row1, textvariable=self.src_var, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=("Segoe UI", 10),
                 width=36).pack(side="left", padx=8)
        self._btn(row1, "📂 Open", self._pick_src, color="#334155").pack(side="left")
        self.page_lbl = tk.Label(row1, text="", bg=BG, fg=SUBTEXT, font=("Segoe UI", 9))
        self.page_lbl.pack(side="left", padx=10)

        # Bookmark list
        list_outer = tk.Frame(f, bg=ACCENT, padx=2, pady=2)
        list_outer.pack(fill="both", expand=True, padx=20, pady=(10, 4))
        list_inner = tk.Frame(list_outer, bg=DROP_BG)
        list_inner.pack(fill="both", expand=True)

        self.hint = tk.Label(list_inner,
                             text="Open a PDF to see its bookmarks",
                             bg=DROP_BG, fg=SUBTEXT, font=("Segoe UI", 10))

        sb = ttk.Scrollbar(list_inner, orient="vertical")
        self.listbox = tk.Listbox(
            list_inner, bg=DROP_BG, fg=TEXT,
            selectbackground=ACCENT, selectforeground="white",
            font=("Consolas", 9), relief="flat", bd=0,
            activestyle="none", height=8, yscrollcommand=sb.set)
        sb.config(command=self.listbox.yview)
        self.listbox.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        sb.pack(side="right", fill="y", pady=6)
        self.hint.place(relx=0.5, rely=0.5, anchor="center")

        # Bookmark actions
        act = tk.Frame(f, bg=BG)
        act.pack(fill="x", padx=20, pady=2)
        self._btn(act, "+ Add Bookmark", self._add_bookmark).pack(side="left", padx=(0, 6))
        self._btn(act, "✕ Delete Selected", self._del_bookmark, color=DANGER).pack(side="left", padx=(0, 6))
        self._btn(act, "💾 Save Changes", self._save_bookmarks, color="#334155").pack(side="left")

        # Separator
        tk.Frame(f, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(10, 6))

        # Split-by-bookmark section
        tk.Label(f, text="Split by bookmark — create one PDF per top-level chapter",
                 bg=BG, fg=TEXT, font=("Segoe UI", 10, "bold")
                 ).pack(anchor="w", padx=20, pady=(0, 4))

        split_row = tk.Frame(f, bg=BG)
        split_row.pack(fill="x", padx=20, pady=3)
        tk.Label(split_row, text="Output folder:", bg=BG, fg=TEXT, width=14, anchor="w").pack(side="left")
        self.split_dir_var = tk.StringVar(value=os.path.expanduser("~/Desktop"))
        tk.Entry(split_row, textvariable=self.split_dir_var, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=("Segoe UI", 10),
                 width=32).pack(side="left", padx=8)
        self._btn(split_row, "📁 Choose", self._pick_split_dir, color="#334155").pack(side="left")

        bot = tk.Frame(f, bg=BG)
        bot.pack(fill="x", padx=20, pady=(8, 12))
        self._btn(bot, "✂  Split by Bookmarks", self._split_by_bookmarks).pack(side="left")
        self.open_btn = self._btn(bot, "📂 Open folder", self._open_split_folder,
                                  color="#334155")
        self.open_btn.pack(side="left", padx=8)
        self.open_btn.pack_forget()
        self.status = tk.Label(bot, text="", bg=BG, font=("Segoe UI", 9))
        self.status.pack(side="left", padx=6)

    # ── Helpers ───────────────────────────────────────────────────────────────

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
            self._src_path = path
            self._load_bookmarks(path)

    def _pick_split_dir(self):
        d = filedialog.askdirectory()
        if d:
            self.split_dir_var.set(d)

    def _open_split_folder(self):
        d = os.path.abspath(self.split_dir_var.get())
        if sys.platform == "win32":
            subprocess.Popen(f'explorer "{d}"')
        elif sys.platform == "darwin":
            subprocess.Popen(["open", d])
        else:
            subprocess.Popen(["xdg-open", d])

    def _load_bookmarks(self, path):
        self.listbox.delete(0, "end")
        self._flat = []
        try:
            self._reader = PdfReader(path)
            n = len(self._reader.pages)
            self.page_lbl.config(text=f"{n} pages")
            self._flatten_outline(self._reader.outline, 0)
            for indent, title, pg in self._flat:
                prefix = "    " * indent
                self.listbox.insert("end", f"{prefix}▸ {title}  (p. {pg + 1})")
            if not self._flat:
                self.listbox.insert("end", "  — no bookmarks found —")
        except Exception as e:
            self._set_status(f"Error loading: {e}", ok=False)
        self._hint_update()

    def _flatten_outline(self, outline, depth):
        for item in outline:
            if isinstance(item, list):
                self._flatten_outline(item, depth + 1)
            else:
                try:
                    pg = self._reader.get_destination_page_number(item)
                except Exception:
                    pg = 0
                self._flat.append((depth, item.title, pg))

    # ── Bookmark editing ──────────────────────────────────────────────────────

    def _add_bookmark(self):
        if not self._reader:
            self._set_status("⚠ Open a PDF first!", ok=False)
            return
        title = simpledialog.askstring("Add Bookmark", "Bookmark title:",
                                       parent=self.frame.winfo_toplevel())
        if not title:
            return
        page_str = simpledialog.askstring("Add Bookmark",
                                          f"Page number (1–{len(self._reader.pages)}):",
                                          parent=self.frame.winfo_toplevel())
        if not page_str:
            return
        try:
            pg = int(page_str) - 1
            if not (0 <= pg < len(self._reader.pages)):
                raise ValueError
        except ValueError:
            self._set_status("⚠ Invalid page number!", ok=False)
            return
        self._flat.append((0, title, pg))
        self.listbox.insert("end", f"▸ {title}  (p. {pg + 1})")
        self._hint_update()
        self._set_status(f"Bookmark added — remember to Save Changes")

    def _del_bookmark(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        i = sel[0]
        if i < len(self._flat):
            self._flat.pop(i)
            self.listbox.delete(i)
            self._hint_update()
            self._set_status("Bookmark removed — remember to Save Changes")

    def _save_bookmarks(self):
        if not self._reader or not self._src_path:
            self._set_status("⚠ Open a PDF first!", ok=False)
            return
        path = filedialog.asksaveasfilename(
            initialdir=os.path.dirname(self._src_path),
            initialfile=os.path.splitext(os.path.basename(self._src_path))[0] + "_bookmarked.pdf",
            defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if not path:
            return
        try:
            writer = PdfWriter()
            for page in self._reader.pages:
                writer.add_page(page)
            for _, title, pg in self._flat:
                writer.add_outline_item(title, pg)
            with open(path, "wb") as fh:
                writer.write(fh)
            self._set_status(f"✓ Saved with {len(self._flat)} bookmark(s)  —  {os.path.basename(path)}")
        except Exception as e:
            self._set_status(f"Error: {e}", ok=False)

    # ── Split by bookmarks ────────────────────────────────────────────────────

    def _split_by_bookmarks(self):
        if not self._reader or not self._src_path:
            self._set_status("⚠ Open a PDF first!", ok=False)
            return
        top_level = [(t, p) for (d, t, p) in self._flat if d == 0]
        if not top_level:
            self._set_status("⚠ No top-level bookmarks found!", ok=False)
            return

        out_dir  = self.split_dir_var.get().strip()
        os.makedirs(out_dir, exist_ok=True)
        total_pg = len(self._reader.pages)

        try:
            for idx, (title, start_pg) in enumerate(top_level):
                end_pg = top_level[idx + 1][1] if idx + 1 < len(top_level) else total_pg
                writer = PdfWriter()
                for pg in range(start_pg, end_pg):
                    writer.add_page(self._reader.pages[pg])
                safe_title = "".join(c for c in title if c.isalnum() or c in " _-").strip()
                fname = f"{idx + 1:02d}_{safe_title or 'chapter'}.pdf"
                with open(os.path.join(out_dir, fname), "wb") as fh:
                    writer.write(fh)

            self._set_status(
                f"✓ Split into {len(top_level)} file(s)  —  {os.path.basename(out_dir)}/")
            self.open_btn.pack(side="left", padx=8)
        except Exception as e:
            self._set_status(f"Error: {e}", ok=False)
            self.open_btn.pack_forget()
