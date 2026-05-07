import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, filedialog

from pypdf import PdfReader, PdfWriter
from config import BG, PANEL, ACCENT, ACCENT2, TEXT, SUBTEXT, DANGER, SUCCESS


class PasswordTab:
    """Tab — Encrypt a PDF with a password, or remove password protection."""

    LABEL = "🔒  Password"

    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text=self.LABEL)
        self._build()

    def _build(self):
        f = self.frame

        tk.Label(f, text="Protect a PDF with a password, or remove existing protection",
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

        self.enc_label = tk.Label(f, text="", bg=BG, fg=SUBTEXT, font=("Segoe UI", 9))
        self.enc_label.pack(anchor="w", padx=20, pady=(2, 0))

        # Mode
        tk.Label(f, text="Action:", bg=BG, fg=TEXT,
                 font=("Segoe UI", 10)).pack(anchor="w", padx=20, pady=(12, 4))
        self.mode_var = tk.StringVar(value="protect")
        mode_row = tk.Frame(f, bg=BG)
        mode_row.pack(anchor="w", padx=36)
        tk.Radiobutton(mode_row, text="🔒  Protect with password", variable=self.mode_var,
                       value="protect", bg=BG, fg=TEXT, selectcolor=ACCENT,
                       activebackground=BG, font=("Segoe UI", 10),
                       command=self._on_mode).pack(side="left", padx=(0, 24))
        tk.Radiobutton(mode_row, text="🔓  Remove password", variable=self.mode_var,
                       value="remove", bg=BG, fg=TEXT, selectcolor=ACCENT,
                       activebackground=BG, font=("Segoe UI", 10),
                       command=self._on_mode).pack(side="left")

        # ── Protect section ───────────────────────────────────────────────────
        self.protect_frame = tk.Frame(f, bg=BG)
        self.protect_frame.pack(fill="x", padx=20, pady=(10, 0))

        for label, attr in [("Open password:", "open_pw"),
                             ("Owner password:", "owner_pw")]:
            row = tk.Frame(self.protect_frame, bg=BG)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label, bg=BG, fg=TEXT, width=16, anchor="w").pack(side="left", padx=(16, 0))
            var = tk.StringVar()
            setattr(self, attr + "_var", var)
            entry = tk.Entry(row, textvariable=var, show="●", bg=PANEL, fg=TEXT,
                             insertbackground=TEXT, relief="flat",
                             font=("Segoe UI", 10), width=22)
            entry.pack(side="left", padx=8)
            setattr(self, attr + "_entry", entry)

        tk.Label(self.protect_frame,
                 text="  Owner password controls permissions (optional — if left empty, same as open password)",
                 bg=BG, fg=SUBTEXT, font=("Segoe UI", 8)).pack(anchor="w", padx=16, pady=(0, 4))

        # Show/hide toggle
        show_row = tk.Frame(self.protect_frame, bg=BG)
        show_row.pack(anchor="w", padx=16)
        self.show_pw = tk.BooleanVar(value=False)
        tk.Checkbutton(show_row, text="Show passwords", variable=self.show_pw,
                       bg=BG, fg=TEXT, selectcolor=PANEL, activebackground=BG,
                       font=("Segoe UI", 9), command=self._toggle_show).pack(side="left")

        # Encryption strength
        alg_row = tk.Frame(self.protect_frame, bg=BG)
        alg_row.pack(fill="x", pady=(8, 2))
        tk.Label(alg_row, text="Encryption:", bg=BG, fg=TEXT, width=16, anchor="w").pack(side="left", padx=(16, 0))
        self.alg_var = tk.StringVar(value="AES-256")
        for lbl, val in [("AES-256  (recommended)", "AES-256"),
                          ("AES-128", "AES-128")]:
            tk.Radiobutton(alg_row, text=lbl, variable=self.alg_var, value=val,
                           bg=BG, fg=TEXT, selectcolor=ACCENT, activebackground=BG,
                           font=("Segoe UI", 10)).pack(side="left", padx=(0, 18))

        # ── Remove section ────────────────────────────────────────────────────
        self.remove_frame = tk.Frame(f, bg=BG)

        rem_row = tk.Frame(self.remove_frame, bg=BG)
        rem_row.pack(fill="x", pady=6)
        tk.Label(rem_row, text="Current password:", bg=BG, fg=TEXT, width=16, anchor="w").pack(side="left", padx=(36, 0))
        self.rem_pw_var = tk.StringVar()
        self.rem_pw_entry = tk.Entry(rem_row, textvariable=self.rem_pw_var, show="●",
                                     bg=PANEL, fg=TEXT, insertbackground=TEXT,
                                     relief="flat", font=("Segoe UI", 10), width=22)
        self.rem_pw_entry.pack(side="left", padx=8)

        show_rem = tk.Frame(self.remove_frame, bg=BG)
        show_rem.pack(anchor="w", padx=36)
        self.show_rem = tk.BooleanVar(value=False)
        tk.Checkbutton(show_rem, text="Show password", variable=self.show_rem,
                       bg=BG, fg=TEXT, selectcolor=PANEL, activebackground=BG,
                       font=("Segoe UI", 9),
                       command=lambda: self.rem_pw_entry.config(
                           show="" if self.show_rem.get() else "●")).pack(side="left")

        # Output file
        out_row = tk.Frame(f, bg=BG)
        out_row.pack(fill="x", padx=20, pady=(14, 4))
        tk.Label(out_row, text="Output file:", bg=BG, fg=TEXT).pack(side="left")
        self.out_var = tk.StringVar(
            value=os.path.join(os.path.expanduser("~/Desktop"), "output.pdf"))
        tk.Entry(out_row, textvariable=self.out_var, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=("Segoe UI", 10),
                 width=34).pack(side="left", padx=8)
        self._btn(out_row, "📁 Save as", self._pick_out, color="#334155").pack(side="left")

        # Run
        bot = tk.Frame(f, bg=BG)
        bot.pack(fill="x", padx=20, pady=(10, 12))
        self.run_btn = self._btn(bot, "🔒  Apply", self._run, w=14)
        self.run_btn.pack(side="left")
        self.open_btn = self._btn(bot, "📂 Open folder", self._open_folder,
                                  color="#334155", w=14)
        self.open_btn.pack(side="left", padx=8)
        self.open_btn.pack_forget()
        self.status = tk.Label(bot, text="", bg=BG, font=("Segoe UI", 9))
        self.status.pack(side="left", padx=6)

        self._on_mode()

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
        protecting = self.mode_var.get() == "protect"
        if protecting:
            self.protect_frame.pack(fill="x", padx=20, pady=(10, 0))
            self.remove_frame.pack_forget()
            self.run_btn.config(text="🔒  Protect PDF")
        else:
            self.remove_frame.pack(fill="x", padx=20, pady=(10, 0))
            self.protect_frame.pack_forget()
            self.run_btn.config(text="🔓  Remove Password")

    def _toggle_show(self):
        show = "" if self.show_pw.get() else "●"
        self.open_pw_entry.config(show=show)
        self.owner_pw_entry.config(show=show)

    def _pick_src(self):
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if path:
            self.src_var.set(path)
            base = os.path.splitext(os.path.basename(path))[0]
            suffix = "_protected" if self.mode_var.get() == "protect" else "_unlocked"
            self.out_var.set(os.path.join(os.path.dirname(path), base + suffix + ".pdf"))
            try:
                reader = PdfReader(path)
                status = "🔒 Encrypted" if reader.is_encrypted else "🔓 Not encrypted"
                self.enc_label.config(text=status)
            except Exception:
                self.enc_label.config(text="")

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

    # ── Actions ───────────────────────────────────────────────────────────────
    def _run(self):
        src = self.src_var.get().strip()
        out = self.out_var.get().strip()

        if not src:
            self._set_status("⚠ Please select a source PDF!", ok=False)
            return

        try:
            if self.mode_var.get() == "protect":
                self._protect(src, out)
            else:
                self._remove(src, out)
        except Exception as e:
            self._set_status(f"Error: {e}", ok=False)
            self.open_btn.pack_forget()

    def _protect(self, src, out):
        user_pw  = self.open_pw_var.get()
        owner_pw = self.owner_pw_var.get() or user_pw

        if not user_pw:
            self._set_status("⚠ Open password cannot be empty!", ok=False)
            return

        reader = PdfReader(src)
        writer = PdfWriter()
        writer.append(reader)
        writer.encrypt(user_password=user_pw,
                       owner_password=owner_pw,
                       algorithm=self.alg_var.get())

        if not out.lower().endswith(".pdf"):
            out += ".pdf"
            self.out_var.set(out)

        with open(out, "wb") as fh:
            writer.write(fh)

        self._set_status(f"✓ Protected with {self.alg_var.get()}  —  {os.path.basename(out)}")
        self.open_btn.pack(side="left", padx=8)

    def _remove(self, src, out):
        password = self.rem_pw_var.get()
        reader   = PdfReader(src)

        if reader.is_encrypted:
            result = reader.decrypt(password)
            if result.value == 0:
                self._set_status("⚠ Wrong password!", ok=False)
                self.open_btn.pack_forget()
                return

        writer = PdfWriter()
        writer.append(reader)

        if not out.lower().endswith(".pdf"):
            out += ".pdf"
            self.out_var.set(out)

        with open(out, "wb") as fh:
            writer.write(fh)

        self._set_status(f"✓ Password removed  —  {os.path.basename(out)}")
        self.open_btn.pack(side="left", padx=8)
