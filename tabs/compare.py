import os
import tkinter as tk
from tkinter import ttk, filedialog

from pypdf import PdfReader
from config import BG, PANEL, ACCENT, ACCENT2, TEXT, SUBTEXT, DANGER, SUCCESS


class CompareTab:
    """Tab — Compare two PDFs page by page and highlight text differences."""

    LABEL = "⚖  Compare PDFs"

    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text=self.LABEL)
        self._build()

    def _build(self):
        f = self.frame

        tk.Label(f, text="Compare two PDFs — find added, removed, and changed text",
                 bg=BG, fg=TEXT, font=("Segoe UI", 10, "bold")
                 ).pack(anchor="w", padx=20, pady=(16, 10))

        # File pickers
        for attr, label in [("a", "PDF A (original):"), ("b", "PDF B (modified):")]:
            row = tk.Frame(f, bg=BG)
            row.pack(fill="x", padx=20, pady=3)
            tk.Label(row, text=label, bg=BG, fg=TEXT, width=18, anchor="w").pack(side="left")
            var = tk.StringVar()
            setattr(self, f"src_{attr}", var)
            tk.Entry(row, textvariable=var, bg=PANEL, fg=TEXT,
                     insertbackground=TEXT, relief="flat", font=("Segoe UI", 10),
                     width=34).pack(side="left", padx=8)
            self._btn(row, "📂 Open",
                      lambda a=attr: self._pick(a),
                      color="#334155").pack(side="left")

        # Run button
        run_row = tk.Frame(f, bg=BG)
        run_row.pack(fill="x", padx=20, pady=(10, 4))
        self._btn(run_row, "⚖  Compare", self._run, w=14).pack(side="left")
        self.status = tk.Label(run_row, text="", bg=BG, font=("Segoe UI", 9))
        self.status.pack(side="left", padx=10)

        # Legend
        leg = tk.Frame(f, bg=BG)
        leg.pack(anchor="w", padx=20, pady=(0, 6))
        for color, label in [("#34d399", "+ Added"), ("#f87171", "- Removed"),
                              ("#fbbf24", "~ Changed page count")]:
            tk.Label(leg, text="██", bg=BG, fg=color,
                     font=("Segoe UI", 11)).pack(side="left", padx=(0, 2))
            tk.Label(leg, text=label, bg=BG, fg=SUBTEXT,
                     font=("Segoe UI", 9)).pack(side="left", padx=(0, 14))

        # Result text box
        result_frame = tk.Frame(f, bg=PANEL, padx=2, pady=2)
        result_frame.pack(fill="both", expand=True, padx=20, pady=(0, 12))

        sb = ttk.Scrollbar(result_frame, orient="vertical")
        self.result = tk.Text(
            result_frame, bg=PANEL, fg=TEXT, font=("Consolas", 9),
            relief="flat", state="disabled", wrap="none",
            padx=10, pady=8, yscrollcommand=sb.set)
        sb.config(command=self.result.yview)
        self.result.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Color tags
        self.result.tag_config("added",   foreground="#34d399")
        self.result.tag_config("removed", foreground="#f87171")
        self.result.tag_config("same",    foreground=SUBTEXT)
        self.result.tag_config("header",  foreground=ACCENT2, font=("Consolas", 9, "bold"))
        self.result.tag_config("meta",    foreground="#fbbf24")

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

    def _pick(self, ab):
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if path:
            getattr(self, f"src_{ab}").set(path)

    def _write(self, text, tag="same"):
        self.result.config(state="normal")
        self.result.insert("end", text, tag)
        self.result.config(state="disabled")

    def _clear(self):
        self.result.config(state="normal")
        self.result.delete("1.0", "end")
        self.result.config(state="disabled")

    def _run(self):
        path_a = self.src_a.get().strip()
        path_b = self.src_b.get().strip()
        if not path_a or not path_b:
            self._set_status("⚠ Please select both PDFs!", ok=False)
            return
        try:
            import difflib
            reader_a = PdfReader(path_a)
            reader_b = PdfReader(path_b)
            pages_a  = len(reader_a.pages)
            pages_b  = len(reader_b.pages)

            self._clear()
            self._write(f"PDF A: {os.path.basename(path_a)}  ({pages_a} pages)\n", "header")
            self._write(f"PDF B: {os.path.basename(path_b)}  ({pages_b} pages)\n", "header")

            if pages_a != pages_b:
                self._write(
                    f"⚠ Page count differs: A={pages_a}, B={pages_b}\n\n", "meta")
            else:
                self._write("\n")

            max_pages = max(pages_a, pages_b)
            diffs_found = 0

            for i in range(max_pages):
                self._write(f"── Page {i + 1} ", "header")

                if i >= pages_a:
                    self._write("(missing in A)\n", "meta")
                    text_b = (reader_b.pages[i].extract_text() or "").splitlines()
                    for line in text_b:
                        self._write(f"+ {line}\n", "added")
                    diffs_found += 1
                    continue
                if i >= pages_b:
                    self._write("(missing in B)\n", "meta")
                    text_a = (reader_a.pages[i].extract_text() or "").splitlines()
                    for line in text_a:
                        self._write(f"- {line}\n", "removed")
                    diffs_found += 1
                    continue

                text_a = (reader_a.pages[i].extract_text() or "").splitlines()
                text_b = (reader_b.pages[i].extract_text() or "").splitlines()

                diff = list(difflib.unified_diff(
                    text_a, text_b, lineterm="", n=1))

                if not diff:
                    self._write("identical ✓\n", "same")
                else:
                    self._write(f"({len(diff)} diff lines)\n", "meta")
                    diffs_found += 1
                    for line in diff[2:]:  # skip the --- +++ header lines
                        if line.startswith("+"):
                            self._write(line + "\n", "added")
                        elif line.startswith("-"):
                            self._write(line + "\n", "removed")
                        else:
                            self._write(line + "\n", "same")

            summary = (f"✓ No differences found"
                       if diffs_found == 0
                       else f"Found differences on {diffs_found} page(s)")
            self._set_status(summary, ok=(diffs_found == 0))

        except Exception as e:
            self._set_status(f"Error: {e}", ok=False)
