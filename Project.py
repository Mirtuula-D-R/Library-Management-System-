"""
Library Management System - GUI version
---------------------------------------
Tkinter desktop app on top of the same MySQL database as the console version.

Setup:
    pip install mysql-connector-python
    (tkinter ships with Python; on Linux: sudo apt install python3-tk)

    -- run once in MySQL as root:
    CREATE DATABASE library;
    CREATE USER 'libraryuser'@'localhost' IDENTIFIED BY 'library123';
    GRANT ALL PRIVILEGES ON library.* TO 'libraryuser'@'localhost';
    FLUSH PRIVILEGES;
"""

import tkinter as tk
from tkinter import ttk, messagebox

import mysql.connector
from mysql.connector.constants import ClientFlag

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "libraryuser",
    "password": "library123",
    "database": "library",
    "client_flags": [ClientFlag.FOUND_ROWS],
}

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    author VARCHAR(100) NOT NULL,
    isbn VARCHAR(20) NOT NULL UNIQUE,
    category VARCHAR(50),
    total_copies INT NOT NULL DEFAULT 1,
    available_copies INT NOT NULL DEFAULT 1
)
"""

COLUMNS = (
    ("id", "ID", 50),
    ("title", "Title", 230),
    ("author", "Author", 160),
    ("isbn", "ISBN", 130),
    ("category", "Category", 110),
    ("total", "Total", 60),
    ("available", "Available", 70),
)


class LibraryApp:
    def __init__(self, root, con):
        self.root = root
        self.con = con
        self.selected_id = None
        self.rows = {}  # id -> original row, so ISBNs keep leading zeros

        root.title("Library Management System")
        root.geometry("900x600")
        root.minsize(820, 520)

        self.vars = {
            "title": tk.StringVar(),
            "author": tk.StringVar(),
            "isbn": tk.StringVar(),
            "category": tk.StringVar(),
            "copies": tk.StringVar(value="1"),
        }
        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Connected to database.")

        self.build_ui()
        self.refresh()

    # ---------- UI ----------
    def build_ui(self):
        header = tk.Label(
            self.root, text="Library Management System",
            font=("Segoe UI", 18, "bold"), bg="#1f3a5f", fg="white", pady=10,
        )
        header.pack(fill="x")

        # Book details form
        form = ttk.LabelFrame(self.root, text="Book Details", padding=10)
        form.pack(fill="x", padx=12, pady=(10, 4))

        fields = [
            ("Title", "title"), ("Author", "author"), ("ISBN", "isbn"),
            ("Category", "category"), ("Copies", "copies"),
        ]
        for i, (label, key) in enumerate(fields):
            row, col = divmod(i, 3)
            ttk.Label(form, text=label + ":").grid(row=row, column=col * 2, sticky="e", padx=(8, 4), pady=4)
            ttk.Entry(form, textvariable=self.vars[key], width=22).grid(row=row, column=col * 2 + 1, pady=4)

        # Action buttons
        buttons = ttk.Frame(self.root, padding=(12, 4))
        buttons.pack(fill="x")
        for text, cmd in [
            ("Add", self.add_book), ("Update", self.update_book),
            ("Delete", self.delete_book), ("Issue", self.issue_book),
            ("Return", self.return_book), ("Clear", self.clear_form),
        ]:
            ttk.Button(buttons, text=text, command=cmd, width=10).pack(side="left", padx=4)

        # Search bar
        search = ttk.Frame(self.root, padding=(12, 6))
        search.pack(fill="x")
        ttk.Label(search, text="Search (title / author / ISBN / category):").pack(side="left")
        entry = ttk.Entry(search, textvariable=self.search_var, width=34)
        entry.pack(side="left", padx=6)
        entry.bind("<Return>", lambda e: self.refresh())
        ttk.Button(search, text="Search", command=self.refresh).pack(side="left", padx=2)
        ttk.Button(search, text="Show All", command=self.show_all).pack(side="left", padx=2)

        # Table
        table_frame = ttk.Frame(self.root, padding=(12, 4))
        table_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(
            table_frame, columns=[c[0] for c in COLUMNS], show="headings", selectmode="browse"
        )
        for key, heading, width in COLUMNS:
            self.tree.heading(key, text=heading)
            self.tree.column(key, width=width, anchor="center" if key in ("id", "total", "available") else "w")
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.tag_configure("out", foreground="#b00020")

        # Status bar
        tk.Label(self.root, textvariable=self.status_var, anchor="w",
                 relief="sunken", padx=8).pack(fill="x", side="bottom")

    # ---------- helpers ----------
    def set_status(self, text):
        self.status_var.set(text)

    def run(self, sql, params=()):
        """Execute a write query and return the affected row count."""
        cur = self.con.cursor()
        try:
            cur.execute(sql, params)
            self.con.commit()
            return cur.rowcount
        finally:
            cur.close()

    def refresh(self):
        term = self.search_var.get().strip()
        sql = ("SELECT id, title, author, isbn, category, total_copies, available_copies "
               "FROM books")
        params = ()
        if term:
            like = f"%{term}%"
            sql += (" WHERE title LIKE %s OR author LIKE %s "
                    "OR isbn LIKE %s OR category LIKE %s")
            params = (like, like, like, like)
        sql += " ORDER BY id"

        cur = self.con.cursor()
        try:
            cur.execute(sql, params)
            rows = cur.fetchall()
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))
            return
        finally:
            cur.close()

        self.tree.delete(*self.tree.get_children())
        self.rows = {row[0]: row for row in rows}
        for row in rows:
            tag = ("out",) if row[6] == 0 else ()
            self.tree.insert("", "end", iid=str(row[0]), values=row, tags=tag)
        self.set_status(f"{len(rows)} book(s) shown." if rows else "No books found.")

    def show_all(self):
        self.search_var.set("")
        self.refresh()

    def clear_form(self):
        for key, var in self.vars.items():
            var.set("1" if key == "copies" else "")
        self.selected_id = None
        self.tree.selection_remove(self.tree.selection())
        self.set_status("Form cleared.")

    def on_select(self, _event):
        selection = self.tree.selection()
        if not selection:
            return
        book_id, title, author, isbn, category, total, _avail = self.rows[int(selection[0])]
        self.selected_id = book_id
        self.vars["title"].set(title)
        self.vars["author"].set(author)
        self.vars["isbn"].set(isbn)
        self.vars["category"].set(category or "")
        self.vars["copies"].set(str(total))

    def read_form(self):
        """Validate and return form values, or None if invalid."""
        title = self.vars["title"].get().strip()
        author = self.vars["author"].get().strip()
        isbn = self.vars["isbn"].get().strip()
        category = self.vars["category"].get().strip()
        if not title or not author or not isbn:
            messagebox.showwarning("Missing details", "Title, Author and ISBN are required.")
            return None
        try:
            copies = int(self.vars["copies"].get())
            if copies < 1:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid copies", "Copies must be a whole number of at least 1.")
            return None
        return title, author, isbn, category, copies

    def need_selection(self):
        if self.selected_id is None:
            messagebox.showinfo("Select a book", "Click a book in the table first.")
            return False
        return True

    # ---------- actions ----------
    def add_book(self):
        data = self.read_form()
        if not data:
            return
        title, author, isbn, category, copies = data
        try:
            self.run(
                "INSERT INTO books (title, author, isbn, category, total_copies, available_copies) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (title, author, isbn, category, copies, copies),
            )
        except mysql.connector.IntegrityError:
            messagebox.showerror("Duplicate ISBN", "A book with this ISBN already exists.")
            return
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))
            return
        self.set_status(f"Added '{title}'.")
        self.clear_form()
        self.refresh()

    def update_book(self):
        if not self.need_selection():
            return
        data = self.read_form()
        if not data:
            return
        title, author, isbn, category, copies = data

        cur = self.con.cursor()
        cur.execute("SELECT total_copies, available_copies FROM books WHERE id = %s", (self.selected_id,))
        row = cur.fetchone()
        cur.close()
        if not row:
            messagebox.showerror("Not found", "That book no longer exists.")
            self.refresh()
            return

        old_total, old_available = row
        new_available = old_available + (copies - old_total)
        if new_available < 0:
            messagebox.showwarning(
                "Too few copies",
                f"{old_total - old_available} copy(ies) are currently issued, "
                f"so total copies cannot be below {old_total - old_available}.",
            )
            return

        try:
            self.run(
                "UPDATE books SET title = %s, author = %s, isbn = %s, category = %s, "
                "total_copies = %s, available_copies = %s WHERE id = %s",
                (title, author, isbn, category, copies, new_available, self.selected_id),
            )
        except mysql.connector.IntegrityError:
            messagebox.showerror("Duplicate ISBN", "Another book already uses this ISBN.")
            return
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))
            return
        self.set_status(f"Updated '{title}'.")
        self.refresh()

    def delete_book(self):
        if not self.need_selection():
            return
        title = self.vars["title"].get()
        if not messagebox.askyesno("Confirm delete", f"Delete '{title}' from the library?"):
            return
        try:
            self.run("DELETE FROM books WHERE id = %s", (self.selected_id,))
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))
            return
        self.set_status(f"Deleted '{title}'.")
        self.clear_form()
        self.refresh()

    def issue_book(self):
        if not self.need_selection():
            return
        try:
            rows = self.run(
                "UPDATE books SET available_copies = available_copies - 1 "
                "WHERE id = %s AND available_copies > 0", (self.selected_id,))
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))
            return
        if rows:
            self.set_status("Book issued successfully.")
        else:
            messagebox.showwarning("Unavailable", "No copies available right now.")
        self.refresh()

    def return_book(self):
        if not self.need_selection():
            return
        try:
            rows = self.run(
                "UPDATE books SET available_copies = available_copies + 1 "
                "WHERE id = %s AND available_copies < total_copies", (self.selected_id,))
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))
            return
        if rows:
            self.set_status("Book returned successfully.")
        else:
            messagebox.showinfo("Nothing to return", "All copies are already in the library.")
        self.refresh()


def main():
    root = tk.Tk()
    try:
        con = mysql.connector.connect(**DB_CONFIG)
        cur = con.cursor()
        cur.execute(CREATE_TABLE_SQL)
        con.commit()
        cur.close()
    except mysql.connector.Error as e:
        messagebox.showerror("Connection Error", f"Could not connect to MySQL:\n{e}")
        root.destroy()
        return

    LibraryApp(root, con)

    def on_close():
        con.close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
