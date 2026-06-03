from tkinter import *
from tkinter import ttk, messagebox
from utils.theme import T, FONT
from utils.widgets import mk_entry, mk_btn, mk_combo, page_header, section_label
from utils.validators import validate_password


def build_user_management_page(parent, get_user_db):
    """Build the user management page."""
    frame = Frame(parent, bg=T["bg"])

    page_header(frame, "User Management", "View and manage system user accounts")

    body = Frame(frame, bg=T["bg"])
    body.pack(fill=BOTH, expand=True, padx=24, pady=16)

    # ── Left: user table ──────────────────────────────────────
    left = Frame(body, bg=T["panel"],
                 highlightthickness=1, highlightbackground=T["border"])
    left.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 12))

    section_label(left, "All System Users")

    tf = Frame(left, bg=T["panel"])
    tf.pack(fill=BOTH, expand=True, padx=16, pady=(0, 16))

    columns = ("Username", "Role", "Created")
    tree = ttk.Treeview(tf, columns=columns, show="headings")
    tree.heading("Username", text="Username")
    tree.heading("Role",     text="Role")
    tree.heading("Created",  text="Created")
    tree.column("Username", width=180, anchor=W, minwidth=100)
    tree.column("Role",     width=130, anchor=W, minwidth=80)
    tree.column("Created",  width=200, anchor=W, minwidth=120)
    sb = ttk.Scrollbar(tf, orient=VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side=LEFT, fill=BOTH, expand=True)
    sb.pack(side=RIGHT, fill=Y)

    # ── Right: detail panel ───────────────────────────────────
    right = Frame(body, bg=T["panel"],
                  highlightthickness=1, highlightbackground=T["border"])
    right.pack(side=LEFT, fill=Y)
    right.columnconfigure(0, weight=1)

    section_label(right, "User Details")

    detail_body = Frame(right, bg=T["panel"])
    detail_body.pack(fill=BOTH, expand=True, padx=16, pady=4)

    def detail_row(label, val="—"):
        row = Frame(detail_body, bg=T["bg"],
                    highlightthickness=1, highlightbackground=T["border"])
        row.pack(fill=X, pady=3)
        Label(row, text=label.upper(), font=FONT["tag"],
              bg=T["bg"], fg=T["muted"],
              width=12, anchor=W).pack(side=LEFT, padx=(10, 6), pady=8)
        lbl = Label(row, text=val, font=FONT["body_b"],
                    bg=T["bg"], fg=T["text"], anchor=W)
        lbl.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        return lbl

    lbl_user  = detail_row("Username")
    lbl_role  = detail_row("Role")
    lbl_cdate = detail_row("Created")
    lbl_login = detail_row("Last Login")

    role_var = StringVar(value="Staff")
    selected_username = StringVar(value="")

    edit_section = Frame(detail_body, bg=T["bg"], pady=8)
    edit_section.pack(fill=X, padx=(10, 0), pady=(10, 0))

    Label(edit_section, text="Edit Account", font=FONT["tag"],
          bg=T["bg"], fg=T["muted"]).pack(anchor=W, pady=(0, 6))

    form = Frame(edit_section, bg=T["bg"])
    form.pack(fill=X)
    form.columnconfigure(1, weight=1)

    Label(form, text="Role", font=FONT["tag"], bg=T["bg"], fg=T["muted"]).grid(
        row=0, column=0, sticky=W, pady=(0, 6), padx=(0, 12))
    role_combo = mk_combo(form, role_var, ["Staff", "Administrator"], width=24)
    role_combo.grid(row=0, column=1, sticky=EW, pady=(0, 6))

    Label(form, text="New Password", font=FONT["tag"], bg=T["bg"], fg=T["muted"]).grid(
        row=1, column=0, sticky=W, pady=(0, 6), padx=(0, 12))
    password_entry = mk_entry(form, width=24, show="●")
    password_entry.grid(row=1, column=1, sticky=EW, pady=(0, 6))

    Label(form, text="Confirm Password", font=FONT["tag"], bg=T["bg"], fg=T["muted"]).grid(
        row=2, column=0, sticky=W, pady=(0, 6), padx=(0, 12))
    confirm_password_entry = mk_entry(form, width=24, show="●")
    confirm_password_entry.grid(row=2, column=1, sticky=EW, pady=(0, 6))

    status_lbl = Label(edit_section, text="", font=FONT["body"],
                       bg=T["bg"], fg=T["success"])
    status_lbl.pack(anchor=W, pady=(4, 0))

    def clear_selection():
        selected_username.set("")
        lbl_user.config(text="—")
        lbl_role.config(text="—")
        lbl_cdate.config(text="—")
        lbl_login.config(text="—")
        role_var.set("Staff")
        password_entry.delete(0, END)
        confirm_password_entry.delete(0, END)
        status_lbl.config(text="")

    def load_users():
        for item in tree.get_children():
            tree.delete(item)
        user_db = get_user_db()
        users = user_db.get_all_users()
        if not users:
            tree.insert("", END, values=("No users found", "—", "—"))
            clear_selection()
            return
        for i, (username, ud) in enumerate(users.items()):
            tag = "even" if i % 2 == 0 else "odd"
            tree.insert("", END, tags=(tag,), values=(
                username,
                ud.get("role", "N/A"),
                ud.get("created_date", "N/A")))
        tree.tag_configure("even", background=T["row_even"])
        tree.tag_configure("odd",  background=T["row_odd"])
        clear_selection()

    def on_select(event):
        sel = tree.selection()
        if not sel:
            return
        item = tree.item(sel)
        username = item["values"][0]
        if username == "No users found":
            return
        user_db = get_user_db()
        ud = user_db.get_user(username)
        if ud:
            selected_username.set(username)
            lbl_user.config(text=username)
            lbl_role.config(text=ud.get("role", "N/A"))
            lbl_cdate.config(text=ud.get("created_date", "N/A"))
            lbl_login.config(text=ud.get("last_login") or "Never")
            role_var.set(ud.get("role", "Staff"))
            password_entry.delete(0, END)
            confirm_password_entry.delete(0, END)
            status_lbl.config(text="")

    def update_user():
        username = selected_username.get()
        if not username:
            messagebox.showwarning("Warning", "Select a user before updating")
            return
        role = role_var.get()
        password = password_entry.get()
        confirm = confirm_password_entry.get()
        if password or confirm:
            if password != confirm:
                messagebox.showerror("Error", "Passwords do not match")
                return
            if not validate_password(password):
                messagebox.showerror("Error", "Password must be at least 6 characters")
                return
        else:
            password = None
        user_db = get_user_db()
        if user_db.update_user(username, role=role, password=password):
            status_lbl.config(text=f"User '{username}' updated successfully", fg=T["success"])
            lbl_role.config(text=role)
            password_entry.delete(0, END)
            confirm_password_entry.delete(0, END)
            load_users()
        else:
            messagebox.showerror("Error", "Unable to update user")

    def delete_user():
        username = selected_username.get()
        if not username:
            messagebox.showwarning("Warning", "Select a user before deleting")
            return
        if not messagebox.askyesno("Confirm Delete",
                                   f"Delete user account '{username}'?\nThis cannot be undone."):
            return
        user_db = get_user_db()
        if user_db.delete_user(username):
            messagebox.showinfo("Deleted", f"User '{username}' deleted successfully")
            clear_selection()
            load_users()
        else:
            messagebox.showerror("Error", "Unable to delete user")

    tree.bind("<<TreeviewSelect>>", on_select)

    bf = Frame(right, bg=T["panel"])
    bf.pack(fill=X, padx=16, pady=(12, 16), anchor=W)
    mk_btn(bf, "Update User", update_user, width=14).pack(side=LEFT, padx=(0, 8))
    mk_btn(bf, "Delete User", delete_user, danger=True, width=14).pack(side=LEFT, padx=(0, 8))
    mk_btn(bf, "⟳  Refresh List", load_users, secondary=True, width=14).pack(side=LEFT)

    load_users()
    return frame
