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
from tabs import (MergeTab, SplitTab, ExtractTextTab, ExtractImagesTab,
                  CompressTab, RotateTab, WatermarkTab, PasswordTab, ReorderTab,
                  MetadataTab, BlankTab, RepairTab, ConvertTab, CropTab, OcrTab, CompareTab,
                  RedactTab, PageNumbersTab, SignatureTab, NupTab, BookmarksTab)

# ── To add a new tool in the future: ─────────────────────────────────────────
# 1. Create  tabs/your_feature.py  with a class  YourFeatureTab
# 2. Add it to  tabs/__init__.py
# 3. Add YourFeatureTab to TAB_CLASSES below
# ─────────────────────────────────────────────────────────────────────────────

TAB_CLASSES = [
    MergeTab, SplitTab, ExtractTextTab, ExtractImagesTab,
    CompressTab, RotateTab, WatermarkTab, PasswordTab, ReorderTab,
    MetadataTab, BlankTab, RepairTab, ConvertTab, CropTab, OcrTab, CompareTab,
    RedactTab, PageNumbersTab, SignatureTab, NupTab, BookmarksTab,
]

COLS = 7   # cards per row


class _ToolContainer(ttk.Frame):
    """Acts as a ttk.Notebook stand-in so tab classes stay unchanged."""
    def __init__(self, parent):
        super().__init__(parent)
        self.tools = []   # list of (frame, label)

    def add(self, frame, text=""):
        self.tools.append((frame, text))
        frame.pack_forget()


class PDFTool(Root):
    def __init__(self):
        super().__init__()
        self.title("PDF Tool")
        self.geometry("860x790")
        self.configure(bg=BG)
        self.resizable(False, False)
        self._current      = None   # currently shown tool frame
        self._active_card  = None   # currently highlighted card widgets
        self._style()
        self._header()
        self._build()

    # ── Style ─────────────────────────────────────────────────────────────────
    def _style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TFrame",     background=BG)
        s.configure("TLabel",     background=BG, foreground=TEXT, font=("Segoe UI", 10))
        s.configure("TScrollbar", background=PANEL, troughcolor=BG,
                    bordercolor=BORDER, arrowcolor=ACCENT2)

    # ── Header ────────────────────────────────────────────────────────────────
    def _header(self):
        bar = tk.Frame(self, bg=PANEL, height=34)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        tk.Label(bar, text="⬡  PDF Tool", bg=PANEL, fg=ACCENT2,
                 font=("Segoe UI", 14, "bold")).pack(side="left", padx=20, pady=3)
        link = tk.Label(bar, text="Todor Vankov", bg=PANEL, fg=ACCENT2,
                        font=("Segoe UI", 9, "underline"), cursor="hand2")
        link.pack(side="right", padx=20)
        link.bind("<Button-1>", lambda e: __import__("webbrowser").open(
            "https://www.todorvankov.com"))

    # ── Build ─────────────────────────────────────────────────────────────────
    def _build(self):
        # ── Card nav (always visible) ─────────────────────────────────────────
        nav = tk.Frame(self, bg=BG)
        nav.pack(fill="x", padx=14, pady=(12, 0))

        self._container = _ToolContainer(self)

        # Instantiate all tools
        for TabClass in TAB_CLASSES:
            TabClass(self._container)

        # Build card grid
        grid = tk.Frame(nav, bg=BG)
        grid.pack()
        for i, (frame, label) in enumerate(self._container.tools):
            parts = label.split("  ", 1)
            icon  = parts[0].strip()
            name  = parts[1].strip() if len(parts) > 1 else label
            row, col = divmod(i, COLS)
            card_widgets = self._make_card(grid, icon, name, frame)
            card_widgets["frame"].grid(row=row, column=col, padx=5, pady=5)

        # ── Separator ─────────────────────────────────────────────────────────
        tk.Frame(self, bg=BORDER, height=2).pack(fill="x", pady=(10, 0))

        # ── Content area ──────────────────────────────────────────────────────
        self._container.pack(fill="both", expand=True)

        # Placeholder shown when no tool is selected
        self._placeholder = tk.Frame(self._container, bg=BG)
        tk.Label(self._placeholder,
                 text="← Select a tool above to get started",
                 bg=BG, fg=SUBTEXT, font=("Segoe UI", 12)
                 ).place(relx=0.5, rely=0.45, anchor="center")
        self._placeholder.pack(fill="both", expand=True)

    # ── Card factory ──────────────────────────────────────────────────────────
    def _make_card(self, parent, icon, name, frame):
        card = tk.Frame(parent, bg=PANEL, width=112, height=68,
                        highlightthickness=2, highlightbackground=BORDER,
                        cursor="hand2")
        card.pack_propagate(False)

        icon_lbl = tk.Label(card, text=icon, bg=PANEL, fg=TEXT,
                            font=("Segoe UI", 16))
        icon_lbl.pack(expand=True, pady=(6, 1))

        name_lbl = tk.Label(card, text=name, bg=PANEL, fg=SUBTEXT,
                            font=("Segoe UI", 8), wraplength=100, justify="center")
        name_lbl.pack(pady=(0, 5))

        widgets = {"frame": card, "icon": icon_lbl, "name": name_lbl}

        def enter(e):
            if self._active_card is not widgets:
                _set_card_style(widgets, "hover")

        def leave(e):
            if self._active_card is not widgets:
                _set_card_style(widgets, "normal")

        def click(e):
            self._show_tool(frame, widgets)

        for w in (card, icon_lbl, name_lbl):
            w.bind("<Enter>", enter)
            w.bind("<Leave>", leave)
            w.bind("<Button-1>", click)

        return widgets

    # ── Navigation ────────────────────────────────────────────────────────────
    def _show_tool(self, frame, card_widgets):
        # Deactivate previous card
        if self._active_card and self._active_card is not card_widgets:
            _set_card_style(self._active_card, "normal")

        # Activate new card
        self._active_card = card_widgets
        _set_card_style(card_widgets, "active")

        # Swap content
        if self._current:
            self._current.pack_forget()
        self._placeholder.pack_forget()

        frame.pack(fill="both", expand=True)
        self._current = frame


# ── Card style helper (module-level so lambdas stay small) ────────────────────
def _set_card_style(w, state):
    styles = {
        "normal": (PANEL,   BORDER, TEXT,      SUBTEXT),
        "hover":  (ACCENT2, ACCENT, "#ffffff",  "#ffffff"),
        "active": (ACCENT,  ACCENT, "#ffffff",  "#ffffff"),
    }
    bg, border, fg_icon, fg_name = styles[state]
    w["frame"].config(bg=bg, highlightbackground=border)
    w["icon"].config(bg=bg, fg=fg_icon)
    w["name"].config(bg=bg, fg=fg_name)


# Import config colors at module level for the helper
from config import PANEL, BORDER, ACCENT, ACCENT2, TEXT, SUBTEXT


if __name__ == "__main__":
    PDFTool().mainloop()
