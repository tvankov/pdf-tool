import tkinter as tk
from tkinter import ttk, messagebox

try:
    from pypdf import PdfWriter
except ImportError:
    messagebox.showerror("Error", "pypdf not installed!\nRun: pip install pypdf")
    raise SystemExit

try:
    from tkinterdnd2 import TkinterDnD
    Root = TkinterDnD.Tk
except ImportError:
    Root = tk.Tk

from config import BG, PANEL, ACCENT, ACCENT2, TEXT, SUBTEXT, BORDER
from tabs import MergeTab, SplitTab, InfoTab

# ── To add a new tab in the future: ──────────────────────────────────────────
# 1. Create  tabs/your_feature.py  with a class  YourFeatureTab
# 2. Add it to  tabs/__init__.py
# 3. Add one line here:  YourFeatureTab(nb)
# ─────────────────────────────────────────────────────────────────────────────

class PDFTool(Root):
    def __init__(self):
        super().__init__()
        self.title("PDF Tool")
        self.geometry("740x590")
        self.configure(bg=BG)
        self.resizable(False, False)
        self._style()
        self._header()
        self._build_tabs()

    def _style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TNotebook",     background=BG,    borderwidth=0)
        s.configure("TNotebook.Tab", background=PANEL, foreground=SUBTEXT,
                    padding=[18, 8], font=("Segoe UI", 10))
        s.map("TNotebook.Tab",
              background=[("selected", ACCENT)],
              foreground=[("selected", "#ffffff")])
        s.configure("TFrame",     background=BG)
        s.configure("TLabel",     background=BG, foreground=TEXT, font=("Segoe UI", 10))
        s.configure("TScrollbar", background=PANEL, troughcolor=BG,
                    bordercolor=BORDER, arrowcolor=ACCENT2)

    def _header(self):
        bar = tk.Frame(self, bg=PANEL, height=54)
        bar.pack(fill="x")
        tk.Label(bar, text="⬡  PDF Tool", bg=PANEL, fg=ACCENT2,
                 font=("Segoe UI", 14, "bold")).pack(side="left", padx=20, pady=12)
        link = tk.Label(bar, text="Todor Vankov", bg=PANEL, fg=ACCENT2,
                        font=("Segoe UI", 9, "underline"), cursor="hand2")
        link.pack(side="right", padx=20)
        link.bind("<Button-1>", lambda e: __import__("webbrowser").open(
            "https://www.todorvankov.com"))

    def _build_tabs(self):
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        MergeTab(nb)   # tabs/merge.py
        SplitTab(nb)   # tabs/split.py
        InfoTab(nb)    # tabs/info.py
        # ← add new tabs here


if __name__ == "__main__":
    PDFTool().mainloop()
