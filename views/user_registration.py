from tkinter import *
from tkinter import messagebox
from utils.theme import T, FONT
from utils.widgets import mk_entry, mk_btn, mk_combo, page_header, section_label
from utils.validators import validate_username, validate_password


def build_user_registration_page(parent, get_user_db):
    """Build the user registration page."""
    frame = Frame(parent, bg=T["bg"])
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(1, weight=1)

    page_header(frame, "Add New User", "Create a new system user account")

    body = Frame(frame, bg=T["bg"])
    body.pack(fill=BOTH, expand=True)
    body.columnconfigure(0, weight=1)
    body.rowconfigure(0, weight=1)

    card = Frame(body, bg=T["panel"],
                 highlightthickness=1, highlightbackground=T["border"])
    card.pack(padx=80, pady=30, ipadx=0, ipady=0, anchor=N, fill=X)

    section_label(card, "Account Details")

    form = Frame(card, bg=T["panel"])
    form.pack(fill=X, padx=20, pady=(0, 8))
    form.columnconfigure(1, weight=1)

    def lf(label, row, show=None):
        Label(form, text=label.upper(), font=FONT["tag"],
              bg=T["panel"], fg=T["muted"]).grid(
            row=row*2, column=0, columnspan=2, sticky=W, pady=(10, 3))
        e = mk_entry(form, width=44, show=show)
        e.grid(row=row*2+1, column=0, columnspan=2, sticky=EW, ipady=8, pady=(0, 2))
        return e

    username_entry = lf("Username", 0)
    password_entry = lf("Password", 1, show="●")
    confirm_entry  = lf("Confirm Password", 2, show="●")

    Label(form, text="ROLE", font=FONT["tag"],
          bg=T["panel"], fg=T["muted"]).grid(row=6, column=0, columnspan=2, sticky=W, pady=(10, 3))
    role_var = StringVar(value="Staff")
    role_combo = mk_combo(form, role_var, ["Staff", "Administrator"], width=42)
    role_combo.grid(row=7, column=0, columnspan=2, sticky=EW, ipady=6, pady=(0, 2))

    status_lbl = Label(card, text="", font=FONT["body"],
                       bg=T["panel"], fg=T["success"])
    status_lbl.pack(anchor=W, padx=20, pady=(6, 0))

    def clear_form():
        username_entry.delete(0, END)
        password_entry.delete(0, END)
        confirm_entry.delete(0, END)
        role_var.set("Staff")
        status_lbl.config(text="")

    def register_user():
        username = username_entry.get().strip()
        password = password_entry.get()
        confirm  = confirm_entry.get()
        role     = role_var.get()
        if not validate_username(username):
            messagebox.showerror("Error", "Username must be 3–20 chars (letters, numbers, underscores)")
            return
        if not validate_password(password):
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return
        user_db = get_user_db()
        success, message = user_db.add_user(username, password, role)
        if success:
            status_lbl.config(text=f"✓  User '{username}' registered as {role}", fg=T["success"])
            clear_form()
        else:
            messagebox.showerror("Error", message)

    bf = Frame(card, bg=T["panel"])
    bf.pack(fill=X, padx=20, pady=(10, 20))
    mk_btn(bf, "Register User", register_user, width=16).pack(side=LEFT, padx=(0, 8))
    mk_btn(bf, "Clear", clear_form, secondary=True, width=10).pack(side=LEFT)

    return frame
