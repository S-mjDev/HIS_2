import re
from datetime import datetime
from tkinter import INSERT, END, TclError


def validate_phone(phone):
    """Validate phone number format."""
    pattern = r'^\d{1}$'
    return re.match(pattern, phone.replace('-', '').replace(' ', ''))


def validate_email(email):
    """Validate email address format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email)


def validate_date(date_text):
    """Validate a date string in MM-DD-YYYY format."""
    formats = [
        "%m-%d-%Y",
        "%m/%d/%Y",
        "%B %d, %Y",
        "%B-%d-%Y",
        "%b %d, %Y",
        "%d %B %Y",
        "%d %b %Y",
        "%Y-%m-%d",       
    ]
    for fmt in formats:
        try:
            datetime.strptime(date_text, fmt)
            return True
        except ValueError:
            continue
    return False


def validate_username(username):
    """Validate username: 3–20 chars, alphanumeric + underscore only."""
    if not username or len(username) < 3 or len(username) > 20:
        return False
    return re.match(r'^[a-zA-Z0-9_]+$', username) is not None


def validate_password(password):
    """Validate password: minimum 6 characters."""
    return len(password) >= 6


def format_birthdate_entry(entry_widget):
    """Automatically format birth date input with hyphens (MM-DD-YYYY)."""
    current = entry_widget.get()
    digits = re.sub(r'[^0-9]', '', current)
    formatted = digits
    if len(digits) > 2:
        formatted = digits[:2] + '-' + digits[2:]
    if len(digits) > 4:
        formatted = digits[:2] + '-' + digits[2:4] + '-' + digits[4:8]
    formatted = formatted[:10]

    if formatted != current:
        cursor = entry_widget.index(INSERT)
        old_hyphens = current[:cursor].count('-')
        entry_widget.delete(0, END)
        entry_widget.insert(0, formatted)
        new_hyphens = formatted[:cursor].count('-')
        new_cursor = cursor + (new_hyphens - old_hyphens)
        if new_cursor > len(formatted):
            new_cursor = len(formatted)
        entry_widget.icursor(new_cursor)


def uppercase_text_widget(text_widget):
    """Convert Text widget input to uppercase."""
    current = text_widget.get("1.0", END)
    upper = current.upper()
    if current != upper:
        cursor = text_widget.index(INSERT)
        text_widget.delete("1.0", END)
        text_widget.insert("1.0", upper)
        try:
            text_widget.mark_set(INSERT, cursor)
        except TclError:
            pass


def uppercase_entry_widget(entry_widget):
    """Convert Entry widget input to uppercase."""
    current = entry_widget.get()
    upper = current.upper()
    if current != upper:
        pos = entry_widget.index(INSERT)
        entry_widget.delete(0, END)
        entry_widget.insert(0, upper)
        entry_widget.icursor(pos)
