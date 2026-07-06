from tkinter import *
from tkinter import messagebox
from threading import Thread
from utils.theme import T, FONT, apply_styles
from utils.widgets import mk_entry
from utils.resources import get_resource_path, set_window_icon


def create_login_window(on_login_success):
    """Build and display the login window. Calls on_login_success(user_data) on success."""
    login_window = Tk()
    login_window.title("Hospital Information System — Login")
    login_window.geometry("480x540")
    login_window.resizable(False, False)
    login_window.update_idletasks()
    width = 480
    height = 540
    x = (login_window.winfo_screenwidth() // 2) - (width // 2)
    y = (login_window.winfo_screenheight() // 2) - (height // 2)
    login_window.geometry(f"{width}x{height}+{x}+{y}")
    login_window.configure(bg=T["bg"])
    set_window_icon(login_window, "qphn.ico")
    apply_styles()

    # Subtle background grid
    bg_canvas = Canvas(login_window, bg=T["bg"], highlightthickness=0)
    bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
    for i in range(0, 480, 32):
        bg_canvas.create_line(i, 0, i, 540, fill=T["border"], width=1)
    for j in range(0, 540, 32):
        bg_canvas.create_line(0, j, 480, j, fill=T["border"], width=1)

    # Card
    card = Frame(login_window, bg=T["panel"],
                 highlightthickness=1, highlightbackground=T["border2"])
    card.place(relx=0.5, rely=0.5, anchor=CENTER, width=380, height=460)

    Frame(card, bg=T["accent"], height=4).pack(fill=X)

    logo_row = Frame(card, bg=T["panel"])
    logo_row.pack(fill=X, padx=36, pady=(28, 0))
    badge = Frame(logo_row, bg=T["accent"], width=46, height=46)
    badge.pack_propagate(False)
    badge.pack(anchor=W)
    Label(badge, text="H", font=("Georgia", 20, "bold"),
          bg=T["accent"], fg=T["white"]).place(relx=0.5, rely=0.5, anchor=CENTER)

    Label(card, text="Hospital Information System",
          font=FONT["h2"], bg=T["panel"], fg=T["text"]).pack(anchor=W, padx=36, pady=(10, 2))
    Label(card, text="Sign in to your account",
          font=FONT["body"], bg=T["panel"], fg=T["muted"]).pack(anchor=W, padx=36)

    Frame(card, bg=T["border"], height=1).pack(fill=X, padx=36, pady=(16, 0))

    form = Frame(card, bg=T["panel"])
    form.pack(fill=X, padx=36, pady=(16, 0))

    Label(form, text="USERNAME", font=FONT["tag"],
          bg=T["panel"], fg=T["muted"]).pack(anchor=W, pady=(0, 4))
    username_entry = mk_entry(form, width=36)
    username_entry.pack(fill=X, ipady=9, pady=(0, 14))
    username_entry.focus()

    Label(form, text="PASSWORD", font=FONT["tag"],
          bg=T["panel"], fg=T["muted"]).pack(anchor=W, pady=(0, 4))
    password_entry = mk_entry(form, width=36, show="●")
    password_entry.pack(fill=X, ipady=9, pady=(0, 22))

    login_button = None  # Will be set below

    def login():
        """Non-blocking login with threading to prevent UI freeze."""
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        # Disable button to prevent multiple login attempts
        login_button.config(state=DISABLED, text="Signing in...")
        login_window.update()
        
        def auth_thread():
            """Run authentication in background thread."""
            from models.user_database import UserDatabase
            try:
                user_db = UserDatabase()
                success, user_data = user_db.authenticate(username, password)
                # Schedule result handling on main thread
                login_window.after(0, lambda: handle_login_result(success, user_data))
            except Exception as e:
                login_window.after(0, lambda: handle_login_result(False, None, str(e)))
        
        def handle_login_result(success, user_data, error_msg=None):
            """Handle login result on main thread."""
            if login_window.winfo_exists():
                if success:
                    login_window.destroy()
                    on_login_success(user_data)
                else:
                    error = error_msg if error_msg else "Invalid username or password"
                    messagebox.showerror("Login Failed", error)
                    login_button.config(state=NORMAL, text="SIGN IN")
        
        Thread(target=auth_thread, daemon=True).start()

    login_button = Button(form, text="SIGN IN", command=login,
           bg=T["accent"], fg=T["white"], font=("Calibri", 11, "bold"),
           activebackground=T["accent_h"], activeforeground=T["white"],
           bd=0, relief=FLAT, pady=12, cursor="hand2")
    login_button.pack(fill=X)

    login_window.bind("<Return>", lambda e: login())

    Label(card, text="Secure  ·  Role-Based Access Control",
          font=FONT["small"], bg=T["panel"], fg=T["border2"]).pack(side=BOTTOM, pady=18)

    login_window.mainloop()
