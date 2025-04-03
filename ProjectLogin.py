import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import mysql.connector
import requests
import json
from tkinter import font as tkfont
from collections import defaultdict


class LibraryManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("THE BOOK HUB - Library Management System")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f8ff")  # Light blue background

        # Custom fonts
        self.title_font = tkfont.Font(family="Helvetica", size=24, weight="bold")
        self.subtitle_font = tkfont.Font(family="Helvetica", size=16)
        self.button_font = tkfont.Font(family="Arial", size=12)
        self.label_font = tkfont.Font(family="Arial", size=12)
        self.entry_font = tkfont.Font(family="Arial", size=12)

        # Style configuration
        self.style = ttk.Style()
        self.style.configure("TButton", font=self.button_font, padding=6)
        self.style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
        self.style.configure("Treeview", font=("Arial", 11), rowheight=25)
        self.style.map("Treeview", background=[('selected', '#347083')])

        # Database connection
        self.mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="Tanish#04",
            database="Librar"
        )
        self.mycursor = self.mydb.cursor()

        # Initialize tables if they don't exist
        self.initialize_tables()

        # Create main menu
        self.create_main_menu()

    def initialize_tables(self):
        # BookRecord with Genre column
        self.mycursor.execute("SHOW TABLES LIKE 'BookRecord'")
        result = self.mycursor.fetchone()
        if not result:
            self.mycursor.execute("""CREATE TABLE BookRecord(
                BookID varchar(10) PRIMARY KEY, 
                BookName varchar(35), 
                Author varchar(30), 
                Publisher varchar(30),
                Genre varchar(30))""")

        # UserRecord table
        self.mycursor.execute("SHOW TABLES LIKE 'UserRecord'")
        result = self.mycursor.fetchone()
        if not result:
            self.mycursor.execute("""CREATE TABLE UserRecord(
                UserID varchar(10) PRIMARY KEY, 
                UserName varchar(20),
                Password varchar(20), 
                BookID varchar(10),
                FOREIGN KEY (BookID) REFERENCES BookRecord(BookID))""")
            default_users = [
                ("100", "Tanish", "6266", None),
                ("101", "Kunal", "1234", None),
                ("102", "Vishal", "3050", None),
                ("103", "Siddhesh", "5010", None)
            ]
            query = "INSERT INTO UserRecord VALUES(%s, %s, %s, %s)"
            for user in default_users:
                self.mycursor.execute(query, user)
            self.mydb.commit()

        # AdminRecord table
        self.mycursor.execute("SHOW TABLES LIKE 'AdminRecord'")
        result = self.mycursor.fetchone()
        if not result:
            self.mycursor.execute("""CREATE TABLE AdminRecord(
                AdminID varchar(10) PRIMARY KEY, 
                Password varchar(20))""")
            default_admins = [
                ("Tanish04", "626"),
                ("Kunal1020", "123"),
                ("Siddesh510", "786"),
                ("Vishal305", "675")
            ]
            query = "INSERT INTO AdminRecord VALUES(%s, %s)"
            for admin in default_admins:
                self.mycursor.execute(query, admin)
            self.mydb.commit()

        # Feedback table
        self.mycursor.execute("SHOW TABLES LIKE 'Feedback'")
        result = self.mycursor.fetchone()
        if not result:
            self.mycursor.execute("""CREATE TABLE Feedback(
                FeedbackID INT AUTO_INCREMENT PRIMARY KEY,
                UserID varchar(10),
                Feedback varchar(100), 
                Rating varchar(10),
                FOREIGN KEY (UserID) REFERENCES UserRecord(UserID))""")

        # UserReadingHistory table for recommendations
        self.mycursor.execute("SHOW TABLES LIKE 'UserReadingHistory'")
        result = self.mycursor.fetchone()
        if not result:
            self.mycursor.execute("""CREATE TABLE UserReadingHistory(
                HistoryID INT AUTO_INCREMENT PRIMARY KEY,
                UserID varchar(10),
                BookID varchar(10),
                Genre varchar(30),
                FOREIGN KEY (UserID) REFERENCES UserRecord(UserID),
                FOREIGN KEY (BookID) REFERENCES BookRecord(BookID))""")
            self.mydb.commit()

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_main_menu(self):
        self.clear_frame()

        # Main container frame
        main_frame = tk.Frame(self.root, bg="#f0f8ff")
        main_frame.pack(expand=True, fill="both", padx=50, pady=50)

        # Title section
        title_frame = tk.Frame(main_frame, bg="#f0f8ff")
        title_frame.pack(pady=(0, 20))

        title_label = tk.Label(title_frame, text="THE BOOK HUB",
                               font=self.title_font, bg="#f0f8ff", fg="#2a52be")
        title_label.pack()

        subtitle_label = tk.Label(title_frame, text="Library Management System",
                                  font=self.subtitle_font, bg="#f0f8ff", fg="#4682b4")
        subtitle_label.pack(pady=(5, 20))

        # Button section
        button_frame = tk.Frame(main_frame, bg="#f0f8ff")
        button_frame.pack(pady=20)

        # Button styling
        button_style = {
            "width": 20,
            "height": 2,
            "font": self.button_font,
            "bg": "#4682b4",
            "fg": "white",
            "activebackground": "#5f9ea0",
            "activeforeground": "white",
            "relief": tk.RAISED,
            "borderwidth": 3
        }

        admin_btn = tk.Button(button_frame, text="Login as Admin",
                              command=self.admin_login, **button_style)
        admin_btn.grid(row=0, column=0, padx=15, pady=15, ipadx=10)

        user_btn = tk.Button(button_frame, text="Login as User",
                             command=self.user_login, **button_style)
        user_btn.grid(row=0, column=1, padx=15, pady=15, ipadx=10)

        exit_btn = tk.Button(button_frame, text="Exit",
                             command=self.root.quit, **button_style)
        exit_btn.grid(row=1, column=0, columnspan=2, pady=15, ipadx=10)

        # Footer
        footer_label = tk.Label(main_frame, text="© THE BOOK HUB - Library Management System",
                                font=("Arial", 10), bg="#f0f8ff", fg="#4682b4")
        footer_label.pack(side="bottom", pady=20)

    def admin_login(self, attempts=0):
        self.clear_frame()

        if attempts >= 3:
            messagebox.showerror("Error", "Too many failed attempts. System will now exit.")
            self.root.quit()
            return

        # Main container
        login_frame = tk.Frame(self.root, bg="#f0f8ff")
        login_frame.pack(expand=True, fill="both", padx=100, pady=50)

        # Title
        title_label = tk.Label(login_frame, text="Admin Login",
                               font=self.title_font, bg="#f0f8ff", fg="#2a52be")
        title_label.pack(pady=(0, 30))

        # Form frame
        form_frame = tk.Frame(login_frame, bg="#f0f8ff")
        form_frame.pack(pady=20)

        # Entry styling
        entry_style = {
            "font": self.entry_font,
            "bg": "white",
            "relief": tk.SUNKEN,
            "borderwidth": 2
        }

        # Labels and entries
        tk.Label(form_frame, text="Admin ID:", font=self.label_font,
                 bg="#f0f8ff").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.admin_id_entry = tk.Entry(form_frame, **entry_style)
        self.admin_id_entry.grid(row=0, column=1, padx=10, pady=10, ipady=5)

        tk.Label(form_frame, text="Password:", font=self.label_font,
                 bg="#f0f8ff").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.admin_pass_entry = tk.Entry(form_frame, show="*", **entry_style)
        self.admin_pass_entry.grid(row=1, column=1, padx=10, pady=10, ipady=5)

        # Button frame
        button_frame = tk.Frame(login_frame, bg="#f0f8ff")
        button_frame.pack(pady=20)

        # Button styling
        btn_style = {
            "width": 15,
            "font": self.button_font,
            "bg": "#4682b4",
            "fg": "white",
            "activebackground": "#5f9ea0",
            "relief": tk.RAISED,
            "borderwidth": 3
        }

        login_btn = tk.Button(button_frame, text="Login",
                              command=lambda: self.verify_admin_login(attempts), **btn_style)
        login_btn.grid(row=0, column=0, padx=15)

        back_btn = tk.Button(button_frame, text="Back",
                             command=self.create_main_menu, **btn_style)
        back_btn.grid(row=0, column=1, padx=15)

    def verify_admin_login(self, attempts):
        admin_id = self.admin_id_entry.get()
        password = self.admin_pass_entry.get()

        self.mycursor.execute("SELECT Password FROM AdminRecord WHERE AdminID=%s", (admin_id,))
        result = self.mycursor.fetchone()

        if result:
            if result[0] == password:
                messagebox.showinfo("Success", f"Welcome {admin_id} to THE BOOK HUB")
                self.admin_menu()
            else:
                messagebox.showerror("Error", "Invalid password!")
                self.admin_login(attempts + 1)
        else:
            messagebox.showerror("Error", "No such admin ID exists!")
            self.admin_login(attempts + 1)

    def admin_menu(self):
        self.clear_frame()

        # Main container
        menu_frame = tk.Frame(self.root, bg="#f0f8ff")
        menu_frame.pack(expand=True, fill="both", padx=50, pady=50)

        # Title
        title_label = tk.Label(menu_frame, text="Admin Menu",
                               font=self.title_font, bg="#f0f8ff", fg="#2a52be")
        title_label.pack(pady=(0, 30))

        # Button frame
        button_frame = tk.Frame(menu_frame, bg="#f0f8ff")
        button_frame.pack(pady=20)

        # Button styling
        btn_style = {
            "width": 20,
            "height": 2,
            "font": self.button_font,
            "bg": "#4682b4",
            "fg": "white",
            "activebackground": "#5f9ea0",
            "relief": tk.RAISED,
            "borderwidth": 3
        }

        buttons = [
            ("Book Management", self.book_management),
            ("User Management", self.user_management),
            ("Admin Management", self.admin_management),
            ("View Feedback", self.view_feedback),
            ("Logout", self.create_main_menu)
        ]

        for i, (text, command) in enumerate(buttons):
            btn = tk.Button(button_frame, text=text, command=command, **btn_style)
            btn.grid(row=i // 2, column=i % 2, padx=15, pady=15, ipadx=10)

    def book_management(self):
        self.clear_frame()

        # Main container
        menu_frame = tk.Frame(self.root, bg="#f0f8ff")
        menu_frame.pack(expand=True, fill="both", padx=50, pady=50)

        # Title
        title_label = tk.Label(menu_frame, text="Book Management",
                               font=self.title_font, bg="#f0f8ff", fg="#2a52be")
        title_label.pack(pady=(0, 30))

        # Button frame
        button_frame = tk.Frame(menu_frame, bg="#f0f8ff")
        button_frame.pack(pady=20)

        # Button styling
        btn_style = {
            "width": 20,
            "height": 2,
            "font": self.button_font,
            "bg": "#4682b4",
            "fg": "white",
            "activebackground": "#5f9ea0",
            "relief": tk.RAISED,
            "borderwidth": 3
        }

        buttons = [
            ("Add Book", self.add_book),
            ("Add from Google", self.add_from_google),
            ("Display Books", self.display_books),
            ("Search Book", self.search_book),
            ("Delete Book", self.delete_book),
            ("Update Book", self.update_book),
            ("Back", self.admin_menu)
        ]

        for i, (text, command) in enumerate(buttons):
            btn = tk.Button(button_frame, text=text, command=command, **btn_style)
            btn.grid(row=i // 3, column=i % 3, padx=15, pady=15, ipadx=10)

    def add_from_google(self):
        self.clear_frame()

        # Main container
        search_frame = tk.Frame(self.root, bg="#f0f8ff")
        search_frame.pack(expand=True, fill="both", padx=100, pady=50)

        # Title
        title_label = tk.Label(search_frame, text="Search Google Books",
                               font=self.title_font, bg="#f0f8ff", fg="#2a52be")
        title_label.pack(pady=(0, 30))

        # Search frame
        search_form = tk.Frame(search_frame, bg="#f0f8ff")
        search_form.pack(pady=20)

        # Entry styling
        entry_style = {
            "font": self.entry_font,
            "bg": "white",
            "relief": tk.SUNKEN,
            "borderwidth": 2
        }

        tk.Label(search_form, text="Search Query:", font=self.label_font,
                 bg="#f0f8ff").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.search_entry = tk.Entry(search_form, **entry_style)
        self.search_entry.grid(row=0, column=1, padx=10, pady=10, ipady=5)

        # Button frame
        button_frame = tk.Frame(search_frame, bg="#f0f8ff")
        button_frame.pack(pady=20)

        # Button styling
        btn_style = {
            "width": 15,
            "font": self.button_font,
            "bg": "#4682b4",
            "fg": "white",
            "activebackground": "#5f9ea0",
            "relief": tk.RAISED,
            "borderwidth": 3
        }

        search_btn = tk.Button(button_frame, text="Search",
                               command=self.search_google_books, **btn_style)
        search_btn.grid(row=0, column=0, padx=15)

        back_btn = tk.Button(button_frame, text="Back",
                             command=self.book_management, **btn_style)
        back_btn.grid(row=0, column=1, padx=15)

        # Results frame (will be populated after search)
        self.results_frame = tk.Frame(search_frame, bg="#f0f8ff")
        self.results_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def search_google_books(self):
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showerror("Error", "Please enter a search query")
            return

        try:
            # Clear previous results
            for widget in self.results_frame.winfo_children():
                widget.destroy()

            # Search Google Books API
            response = requests.get(
                "https://www.googleapis.com/books/v1/volumes",
                params={"q": query, "maxResults": 10}
            )
            response.raise_for_status()
            data = response.json()

            if not data.get("items"):
                tk.Label(self.results_frame, text="No books found",
                         font=self.label_font, bg="#f0f8ff").pack()
                return

            # Create a scrollable frame for results
            canvas = tk.Canvas(self.results_frame, bg="#f0f8ff")
            scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg="#f0f8ff")

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(
                    scrollregion=canvas.bbox("all")
                )
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # Display each book result
            for i, item in enumerate(data["items"]):
                book_info = item.get("volumeInfo", {})
                title = book_info.get("title", "No title")
                authors = ", ".join(book_info.get("authors", ["Unknown"]))
                publisher = book_info.get("publisher", "Unknown")
                categories = book_info.get("categories", ["General"])
                genre = categories[0] if categories else "General"

                # Create a frame for each book
                book_frame = tk.Frame(scrollable_frame, bg="#e6f2ff" if i % 2 == 0 else "#f0f8ff",
                                      padx=10, pady=10, relief=tk.RAISED, borderwidth=1)
                book_frame.pack(fill="x", padx=5, pady=5)

                # Book info
                tk.Label(book_frame, text=f"Title: {title}",
                         font=self.label_font, bg=book_frame["bg"], anchor="w").pack(anchor="w")
                tk.Label(book_frame, text=f"Author(s): {authors}",
                         font=self.label_font, bg=book_frame["bg"], anchor="w").pack(anchor="w")
                tk.Label(book_frame, text=f"Publisher: {publisher}",
                         font=self.label_font, bg=book_frame["bg"], anchor="w").pack(anchor="w")
                tk.Label(book_frame, text=f"Genre: {genre}",
                         font=self.label_font, bg=book_frame["bg"], anchor="w").pack(anchor="w")

                # Add button
                add_btn = tk.Button(book_frame, text="Add to Library",
                                    command=lambda b=book_info: self.add_google_book(b),
                                    **{
                                        "font": self.button_font,
                                        "bg": "#5f9ea0",
                                        "fg": "white",
                                        "activebackground": "#4682b4",
                                        "relief": tk.RAISED,
                                        "borderwidth": 2
                                    })
                add_btn.pack(pady=5)

        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to search Google Books: {e}")

    def add_google_book(self, book_info):
        # Create a popup window to confirm and get Book ID
        add_window = tk.Toplevel(self.root)
        add_window.title("Add Book from Google")
        add_window.configure(bg="#f0f8ff")
        add_window.geometry("500x400")

        # Title
        tk.Label(add_window, text="Add Book to Library",
                 font=self.title_font, bg="#f0f8ff", fg="#2a52be").pack(pady=(10, 20))

        # Book info display
        info_frame = tk.Frame(add_window, bg="#f0f8ff")
        info_frame.pack(pady=10, padx=20)

        title = book_info.get("title", "No title")
        authors = ", ".join(book_info.get("authors", ["Unknown"]))
        publisher = book_info.get("publisher", "Unknown")
        categories = book_info.get("categories", ["General"])
        genre = categories[0] if categories else "General"

        tk.Label(info_frame, text=f"Title: {title}",
                 font=self.label_font, bg="#f0f8ff", anchor="w").grid(row=0, column=0, sticky="w")
        tk.Label(info_frame, text=f"Author(s): {authors}",
                 font=self.label_font, bg="#f0f8ff", anchor="w").grid(row=1, column=0, sticky="w")
        tk.Label(info_frame, text=f"Publisher: {publisher}",
                 font=self.label_font, bg="#f0f8ff", anchor="w").grid(row=2, column=0, sticky="w")
        tk.Label(info_frame, text=f"Genre: {genre}",
                 font=self.label_font, bg="#f0f8ff", anchor="w").grid(row=3, column=0, sticky="w")

        # Form frame
        form_frame = tk.Frame(add_window, bg="#f0f8ff")
        form_frame.pack(pady=20)

        # Entry styling
        entry_style = {
            "font": self.entry_font,
            "bg": "white",
            "relief": tk.SUNKEN,
            "borderwidth": 2
        }

        tk.Label(form_frame, text="Book ID:", font=self.label_font,
                 bg="#f0f8ff").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        book_id_entry = tk.Entry(form_frame, **entry_style)
        book_id_entry.grid(row=0, column=1, padx=10, pady=10, ipady=5)

        # Button frame
        button_frame = tk.Frame(add_window, bg="#f0f8ff")
        button_frame.pack(pady=20)

        # Button styling
        btn_style = {
            "width": 15,
            "font": self.button_font,
            "bg": "#4682b4",
            "fg": "white",
            "activebackground": "#5f9ea0",
            "relief": tk.RAISED,
            "borderwidth": 3
        }

        def submit_google_book():
            book_id = book_id_entry.get().strip()
            if not book_id:
                messagebox.showerror("Error", "Book ID is required!")
                return

            # Check if book ID already exists
            self.mycursor.execute("SELECT BookID FROM BookRecord WHERE BookID=%s", (book_id,))
            if self.mycursor.fetchone():
                messagebox.showerror("Error", "Book ID already exists!")
                return

            try:
                # Insert the book into the database
                self.mycursor.execute(
                    "INSERT INTO BookRecord VALUES (%s, %s, %s, %s, %s)",
                    (book_id, title, authors, publisher, genre)
                )
                self.mydb.commit()
                messagebox.showinfo("Success", "Book added successfully!")
                add_window.destroy()
                self.book_management()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Failed to add book: {err}")

        submit_btn = tk.Button(button_frame, text="Submit",
                               command=submit_google_book, **btn_style)
        submit_btn.pack()

    def add_book(self):
        self.clear_frame()

        # Main container
        add_frame = tk.Frame(self.root, bg="#f0f8ff")
        add_frame.pack(expand=True, fill="both", padx=100, pady=50)

        # Title
        title_label = tk.Label(add_frame, text="Add New Book",
                               font=self.title_font, bg="#f0f8ff", fg="#2a52be")
        title_label.pack(pady=(0, 30))

        # Form frame
        form_frame = tk.Frame(add_frame, bg="#f0f8ff")
        form_frame.pack(pady=20)

        # Entry styling
        entry_style = {
            "font": self.entry_font,
            "bg": "white",
            "relief": tk.SUNKEN,
            "borderwidth": 2
        }

        labels = ["Book ID:", "Book Name:", "Author:", "Publisher:", "Genre:"]
        self.entries = []

        for i, label in enumerate(labels):
            tk.Label(form_frame, text=label, font=self.label_font,
                     bg="#f0f8ff").grid(row=i, column=0, padx=10, pady=10, sticky="e")
            entry = tk.Entry(form_frame, **entry_style)
            entry.grid(row=i, column=1, padx=10, pady=10, ipady=5)
            self.entries.append(entry)

        # Button frame
        button_frame = tk.Frame(add_frame, bg="#f0f8ff")
        button_frame.pack(pady=20)

        # Button styling
        btn_style = {
            "width": 15,
            "font": self.button_font,
            "bg": "#4682b4",
            "fg": "white",
            "activebackground": "#5f9ea0",
            "relief": tk.RAISED,
            "borderwidth": 3
        }

        submit_btn = tk.Button(button_frame, text="Submit",
                               command=self.submit_book, **btn_style)
        submit_btn.grid(row=0, column=0, padx=15)

        back_btn = tk.Button(button_frame, text="Back",
                             command=self.book_management, **btn_style)
        back_btn.grid(row=0, column=1, padx=15)

    def submit_book(self):
        book_id = self.entries[0].get()
        book_name = self.entries[1].get()
        author = self.entries[2].get()
        publisher = self.entries[3].get()
        genre = self.entries[4].get()

        if not all([book_id, book_name, author, publisher, genre]):
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            self.mycursor.execute("INSERT INTO BookRecord VALUES (%s, %s, %s, %s, %s)",
                                  (book_id, book_name, author, publisher, genre))
            self.mydb.commit()
            messagebox.showinfo("Success", "Book added successfully!")
            self.book_management()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Failed to add book: {err}")

    def display_books(self):
        self.clear_frame()

        # Main container
        display_frame = tk.Frame(self.root, bg="#f0f8ff")
        display_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Title
        title_label = tk.Label(display_frame, text="Book Records",
                               font=self.title_font, bg="#f0f8ff", fg="#2a52be")
        title_label.pack(pady=(0, 20))

        # Treeview frame
        tree_frame = tk.Frame(display_frame, bg="#f0f8ff")
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Create Treeview with style
        tree = ttk.Treeview(tree_frame, columns=("ID", "Name", "Author", "Publisher", "Genre", "Issued To", "User ID"),
                            show="headings")

        # Define headings
        tree.heading("ID", text="Book ID")
        tree.heading("Name", text="Book Name")
        tree.heading("Author", text="Author")
        tree.heading("Publisher", text="Publisher")
        tree.heading("Genre", text="Genre")
        tree.heading("Issued To", text="Issued To")
        tree.heading("User ID", text="User ID")

        # Set column widths
        tree.column("ID", width=100, anchor="center")
        tree.column("Name", width=150, anchor="w")
        tree.column("Author", width=150, anchor="w")
        tree.column("Publisher", width=150, anchor="w")
        tree.column("Genre", width=100, anchor="w")
        tree.column("Issued To", width=150, anchor="w")
        tree.column("User ID", width=100, anchor="center")

        # Add striped row coloring
        tree.tag_configure('oddrow', background="#e6f2ff")
        tree.tag_configure('evenrow', background="#f0f8ff")

        # Get data from database
        self.mycursor.execute("""SELECT BookRecord.BookID, BookRecord.BookName, BookRecord.Author, 
                                BookRecord.Publisher, BookRecord.Genre,
                                UserRecord.UserName, UserRecord.UserID
                                FROM BookRecord
                                LEFT JOIN UserRecord ON BookRecord.BookID=UserRecord.BookID""")
        books = self.mycursor.fetchall()

        # Insert data into treeview with alternating colors
        for i, book in enumerate(books):
            if i % 2 == 0:
                tree.insert("", "end", values=book, tags=('evenrow',))
            else:
                tree.insert("", "end", values=book, tags=('oddrow',))

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(fill="both", expand=True)

        # Button frame
        button_frame = tk.Frame(display_frame, bg="#f0f8ff")
        button_frame.pack(pady=20)

        # Button styling
        btn_style = {
            "width": 15,
            "font": self.button_font,
            "bg": "#4682b4",
            "fg": "white",
            "activebackground": "#5f9ea0",
            "relief": tk.RAISED,
            "borderwidth": 3
        }

        back_btn = tk.Button(button_frame, text="Back",
                             command=self.book_management, **btn_style)
        back_btn.pack()

    def search_book(self):
        book_id = simpledialog.askstring("Search Book", "Enter Book ID:", parent=self.root)
        if not book_id:
            return

        self.mycursor.execute("""SELECT BookRecord.BookID, BookRecord.BookName, BookRecord.Author, 
                                BookRecord.Publisher, BookRecord.Genre,
                                UserRecord.UserName, UserRecord.UserID
                                FROM BookRecord
                                LEFT JOIN UserRecord ON BookRecord.BookID=UserRecord.BookID
                                WHERE BookRecord.BookID=%s""", (book_id,))
        book = self.mycursor.fetchone()

        if book:
            result_window = tk.Toplevel(self.root)
            result_window.title("Book Details")
            result_window.configure(bg="#f0f8ff")
            result_window.geometry("500x350")

            # Title
            tk.Label(result_window, text="Book Details",
                     font=self.title_font, bg="#f0f8ff", fg="#2a52be").pack(pady=(10, 20))

            # Details frame
            details_frame = tk.Frame(result_window, bg="#f0f8ff")
            details_frame.pack(pady=10, padx=20)

            labels = ["Book ID:", "Book Name:", "Author:", "Publisher:", "Genre:", "Issued To:", "User ID:"]

            for i, (label, value) in enumerate(zip(labels, book)):
                tk.Label(details_frame, text=label, font=self.label_font,
                         bg="#f0f8ff", fg="#4682b4").grid(row=i, column=0, padx=10, pady=5, sticky="e")
                tk.Label(details_frame, text=value if value else "Not issued",
                         font=self.label_font, bg="#f0f8ff").grid(row=i, column=1, padx=10, pady=5, sticky="w")
        else:
            messagebox.showerror("Error", "Book not found!")

    def delete_book(self):
        book_id = simpledialog.askstring("Delete Book", "Enter Book ID to delete:", parent=self.root)
        if not book_id:
            return

        try:
            self.mycursor.execute("DELETE FROM BookRecord WHERE BookID=%s", (book_id,))
            if self.mycursor.rowcount > 0:
                self.mydb.commit()
                messagebox.showinfo("Success", "Book deleted successfully!")
            else:
                messagebox.showerror("Error", "Book not found!")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Failed to delete book: {err}")

    def update_book(self):
        book_id = simpledialog.askstring("Update Book", "Enter Book ID to update:", parent=self.root)
        if not book_id:
            return

        # Check if book exists
        self.mycursor.execute("SELECT * FROM BookRecord WHERE BookID=%s", (book_id,))
        book = self.mycursor.fetchone()

        if not book:
            messagebox.showerror("Error", "Book not found!")
            return

        # Create update window
        update_window = tk.Toplevel(self.root)
        update_window.title("Update Book")
        update_window.configure(bg="#f0f8ff")
        update_window.geometry("400x400")

        # Title
        tk.Label(update_window, text="Update Book Details",
                 font=self.title_font, bg="#f0f8ff", fg="#2a52be").pack(pady=(10, 20))

        # Form frame
        form_frame = tk.Frame(update_window, bg="#f0f8ff")
        form_frame.pack(pady=10, padx=20)

        labels = ["Book Name:", "Author:", "Publisher:", "Genre:"]
        current_values = book[1:]  # Skip BookID
        entries = []

        # Entry styling
        entry_style = {
            "font": self.entry_font,
            "bg": "white",
            "relief": tk.SUNKEN,
            "borderwidth": 2
        }

        for i, (label, value) in enumerate(zip(labels, current_values)):
            tk.Label(form_frame, text=label, font=self.label_font,
                     bg="#f0f8ff").grid(row=i, column=0, padx=10, pady=10, sticky="e")
            entry = tk.Entry(form_frame, **entry_style)
            entry.insert(0, value)
            entry.grid(row=i, column=1, padx=10, pady=10, ipady=5)
            entries.append(entry)

        # Button frame
        button_frame = tk.Frame(update_window, bg="#f0f8ff")
        button_frame.pack(pady=20)

        # Button styling
        btn_style = {
            "width": 15,
            "font": self.button_font,
            "bg": "#4682b4",
            "fg": "white",
            "activebackground": "#5f9ea0",
            "relief": tk.RAISED,
            "borderwidth": 3
        }

        def submit_update():
            new_values = [entry.get() for entry in entries]
            if not all(new_values):
                messagebox.showerror("Error", "All fields are required!")
                return

            try:
                self.mycursor.execute(
                    "UPDATE BookRecord SET BookName=%s, Author=%s, Publisher=%s, Genre=%s WHERE BookID=%s",
                    (new_values[0], new_values[1], new_values[2], new_values[3], book_id))
                self.mydb.commit()
                messagebox.showinfo("Success", "Book updated successfully!")
                update_window.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Failed to update book: {err}")

        submit_btn = tk.Button(button_frame, text="Submit", command=submit_update, **btn_style)
        submit_btn.pack()

    def user_management(self):
        self.clear_frame()

        # Main container
        menu_frame = tk.Frame(self.root, bg="#f0f8ff")
        menu_frame.pack(expand=True, fill="both", padx=50, pady=50)

        # Title
        title_label = tk.Label(menu_frame, text="User Management",
                               font=self.title_font, bg="#f0f8ff", fg="#2a52be")
        title_label.pack(pady=(0, 30))

        # Button frame
        button_frame = tk.Frame(menu_frame, bg="#f0f8ff")
        button_frame.pack(pady=20)

        # Button styling
        btn_style = {
            "width": 15,
            "height": 2,
            "font": self.button_font,
            "bg": "#4682b4",
            "fg": "white",
            "activebackground": "#5f9ea0",
            "relief": tk.RAISED,
            "borderwidth": 3
        }

        buttons = [
            ("Add User", self.add_user),
            ("Display Users", self.display_users),
            ("Search User", self.search_user),
            ("Delete User", self.delete_user),
            ("Update User", self.update_user),
            ("Back", self.admin_menu)
        ]

        for i, (text, command) in enumerate(buttons):
            btn = tk.Button(button_frame, text=text, command=command, **btn_style)
            btn.grid(row=i // 3, column=i % 3, padx=15, pady=15, ipadx=10)

    def add_user(self):
        self.clear_frame()

        # Main container
        add_frame = tk.Frame(self.root, bg="#f0f8ff")
        add_frame.pack(expand=True, fill="both", padx=100, pady=50)

        # Title
        title_label = tk.Label(add_frame, text="Add New User",
                               font=self.title_font, bg="#f0f8ff", fg="#2a52be")
        title_label.pack(pady=(0, 30))

        # Form frame
        form_frame = tk.Frame(add_frame, bg="#f0f8ff")
        form_frame.pack(pady=20)

        # Entry styling
        entry_style = {
            "font": self.entry_font,
            "bg": "white",
            "relief": tk.SUNKEN,
            "borderwidth": 2
        }

        labels = ["User ID:", "User Name:", "Password:"]
        self.user_entries = []

        for i, label in enumerate(labels):
            tk.Label(form_frame, text=label, font=self.label_font,
                     bg="#f0f8ff").grid(row=i, column=0, padx=10, pady=10, sticky="e")
            entry = tk.Entry(form_frame, **entry_style)
            entry.grid(row=i, column=1, padx=10, pady=10, ipady=5)
            self.user_entries.append(entry)

        # Button frame
        button_frame = tk.Frame(add_frame, bg="#f0f8ff")
        button_frame.pack(pady=20)

        # Button styling
        btn_style = {
            "width": 15,
            "font": self.button_font,
            "bg": "#4682b4",
            "fg": "white",
            "activebackground": "#5f9ea0",
            "relief": tk.RAISED,
            "borderwidth": 3
        }

        submit_btn = tk.Button(button_frame, text="Submit",
                               command=self.submit_user, **btn_style)
        submit_btn.grid(row=0, column=0, padx=15)

        back_btn = tk.Button(button_frame, text="Back",
                             command=self.user_management, **btn_style)
        back_btn.grid(row=0, column=1, padx=15)

    def submit_user(self):
        user_id = self.user_entries[0].get()
        user_name = self.user_entries[1].get()
        password = self.user_entries[2].get()

        if not all([user_id, user_name, password]):
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            self.mycursor.execute("INSERT INTO UserRecord (UserID, UserName, Password, BookID) VALUES (%s, %s, %s, %s)",
                                  (user_id, user_name, password, None))
            self.mydb.commit()
            messagebox.showinfo("Success", "User added successfully!")
            self.user_management()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Failed to add user: {err}")

    def display_users(self):
        self.clear_frame()

        # Main container
        display_frame = tk.Frame(self.root, bg="#f0f8ff")
        display_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Title
        title_label = tk.Label(display_frame, text="User Records",
                               font=self.title_font, bg="#f0f8ff", fg="#2a52be")
        title_label.pack(pady=(0, 20))

        # Treeview frame
        tree_frame = tk.Frame(display_frame, bg="#f0f8ff")
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Create Treeview
        tree = ttk.Treeview(tree_frame, columns=("ID", "Name", "Password", "Book Issued", "Book ID"), show="headings")

        # Define headings
        tree.heading("ID", text="User ID")
        tree.heading("Name", text="User Name")
        tree.heading("Password", text="Password")
        tree.heading("Book Issued", text="Book Issued")
        tree.heading("Book ID", text="Book ID")

        # Set column widths
        tree.column("ID", width=100, anchor="center")
        tree.column("Name", width=150, anchor="w")
        tree.column("Password", width=100, anchor="center")
        tree.column("Book Issued", width=150, anchor="w")
        tree.column("Book ID", width=100, anchor="center")

        # Add striped row coloring
        tree.tag_configure('oddrow', background="#e6f2ff")
        tree.tag_configure('evenrow', background="#f0f8ff")

        # Get data from database
        self.mycursor.execute("""SELECT UserRecord.UserID, UserRecord.UserName, UserRecord.Password, 
                                BookRecord.BookName, BookRecord.BookID
                                FROM UserRecord
                                LEFT JOIN BookRecord ON UserRecord.BookID=BookRecord.BookID""")
        users = self.mycursor.fetchall()

        # Insert data into treeview with alternating colors
        for i, user in enumerate(users):
            if i % 2 == 0:
                tree.insert("", "end", values=user, tags=('evenrow',))
            else:
                tree.insert("", "end", values=user, tags=('oddrow',))

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(fill="both", expand=True)

        # Button frame
        button_frame = tk.Frame(display_frame, bg="#f0f8ff")
        button_frame.pack(pady=20)

        # Button styling
        btn_style = {
            "width": 15,
            "font": self.button_font,
            "bg": "#4682b4",
            "fg": "white",
            "activebackground": "#5f9ea0",
            "relief": tk.RAISED,
            "borderwidth": 3
        }

        back_btn = tk.Button(button_frame, text="Back",
                             command=self.user_management, **btn_style)
        back_btn.pack()

    def search_user(self):
        user_id = simpledialog.askstring("Search User", "Enter User ID:", parent=self.root)
        if not user_id:
            return

        self.mycursor.execute("""SELECT UserRecord.UserID, UserRecord.UserName, UserRecord.Password, 
                                BookRecord.BookName, BookRecord.BookID
                                FROM UserRecord
                                LEFT JOIN BookRecord ON UserRecord.BookID=BookRecord.BookID
                                WHERE UserRecord.UserID=%s""", (user_id,))
        user = self.mycursor.fetchone()

        if user:
            result_window = tk.Toplevel(self.root)
            result_window.title("User Details")
            result_window.configure(bg="#f0f8ff")
            result_window.geometry("500x300")

            # Title
            tk.Label(result_window, text="User Details",
                     font=self.title_font, bg="#f0f8ff", fg="#2a52be").pack(pady=(10, 20))

            # Details frame
            details_frame = tk.Frame(result_window, bg="#f0f8ff")
            details_frame.pack(pady=10, padx=20)

            labels = ["User ID:", "User Name:", "Password:", "Book Issued:", "Book ID:"]

            for i, (label, value) in enumerate(zip(labels, user)):
                tk.Label(details_frame, text=label, font=self.label_font,
                         bg="#f0f8ff", fg="#4682b4").grid(row=i, column=0, padx=10, pady=5, sticky="e")
                tk.Label(details_frame, text=value if value else "None",
                         font=self.label_font, bg="#f0f8ff").grid(row=i, column=1, padx=10, pady=5, sticky="w")
        else:
            messagebox.showerror("Error", "User not found!")

    def delete_user(self):
        user_id = simpledialog.askstring("Delete User", "Enter User ID to delete:", parent=self.root)
        if not user_id:
            return

        try:
            self.mycursor.execute("DELETE FROM UserRecord WHERE UserID=%s", (user_id,))
            if self.mycursor.rowcount > 0:
                self.mydb.commit()
                messagebox.showinfo("Success", "User deleted successfully!")
            else:
                messagebox.showerror("Error", "User not found!")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Failed to delete user: {err}")

    def update_user(self):
        user_id = simpledialog.askstring("Update User", "Enter User ID to update:", parent=self.root)
        if not user_id:
            return

        # Check if user exists
        self.mycursor.execute("SELECT * FROM UserRecord WHERE UserID=%s", (user_id,))
        user = self.mycursor.fetchone()

        if not user:
            messagebox.showerror("Error", "User not found!")
            return

        # Create update window
        update_window = tk.Toplevel(self.root)
        update_window.title("Update User")
        update_window.configure(bg="#f0f8ff")
        update_window.geometry("400x300")

        # Title
        tk.Label(update_window, text="Update User Details",
                 font=self.title_font, bg="#f0f8ff", fg="#2a52be").pack(pady=(10, 20))

        # Form frame
        form_frame = tk.Frame(update_window, bg="#f0f8ff")
        form_frame.pack(pady=10, padx=20)

        labels = ["User Name:", "Password:"]
        current_values = user[1:3]  # Skip UserID and get Name and Password

        # Entry styling
        entry_style = {
            "font": self.entry_font,
            "bg": "white",
            "relief": tk.SUNKEN,
            "borderwidth": 2
        }

        entries = []
        for i, (label, value) in enumerate(zip(labels, current_values)):
            tk.Label(form_frame, text=label, font=self.label_font,
                     bg="#f0f8ff").grid(row=i, column=0, padx=10, pady=10, sticky="e")
            entry = tk.Entry(form_frame, **entry_style)
            entry.insert(0, value)
            entry.grid(row=i, column=1, padx=10, pady=10, ipady=5)
            entries.append(entry)

        # Button frame
        button_frame = tk.Frame(update_window, bg="#f0f8ff")
        button_frame.pack(pady=20)

        # Button styling
        btn_style = {
            "width": 15,
            "font": self.button_font,
            "bg": "#4682b4",
            "fg": "white",
            "activebackground": "#5f9ea0",
            "relief": tk.RAISED,
            "borderwidth": 3
        }

        def submit_update():
            new_values = [entry.get() for entry in entries]
            if not all(new_values):
                messagebox.showerror("Error", "All fields are required!")
                return

            try:
                self.mycursor.execute("UPDATE UserRecord SET UserName=%s, Password=%s WHERE UserID=%s",
                                      (new_values[0], new_values[1], user_id))
                self.mydb.commit()
                messagebox.showinfo("Success", "User updated successfully!")
                update_window.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Failed to update user: {err}")

        submit_btn = tk.Button(button_frame, text="Submit", command=submit_update, **btn_style)
        submit_btn.pack()

    def admin_management(self):
        self.clear_frame()

        # Main container
        menu_frame = tk.Frame(self.root, bg="#f0f8ff")
        menu_frame.pack(expand=True, fill="both", padx=50, pady=50)

        # Title
        title_label = tk.Label(menu_frame, text="Admin Management",
                               font=self.title_font, bg="#f0f8ff", fg="#2a52be")
        title_label.pack(pady=(0, 30))

        # Button frame
        button_frame = tk.Frame(menu_frame, bg="#f0f8ff")
        button_frame.pack(pady=20)

        # Button styling
        btn_style = {
            "width": 15,
            "height": 2,
            "font": self.button_font,
            "bg": "#4682b4",
            "fg": "white",
            "activebackground": "#5f9ea0",
            "relief": tk.RAISED,
            "borderwidth": 3
        }

        buttons = [
            ("Add Admin", self.add_admin),
            ("Display Admins", self.display_admins),
            ("Search Admin", self.search_admin),
            ("Delete Admin", self.delete_admin),
            ("Update Admin", self.update_admin),
            ("Back", self.admin_menu)
        ]

        for i, (text, command) in enumerate(buttons):
            btn = tk.Button(button_frame, text=text, command=command, **btn_style)
            btn.grid(row=i // 3, column=i % 3, padx=15, pady=15, ipadx=10)

    def add_admin(self):
        self.clear_frame()

        # Main container
        add_frame = tk.Frame(self.root, bg="#f0f8ff")
        add_frame.pack(expand=True, fill="both", padx=100, pady=50)

        # Title
        title_label = tk.Label(add_frame, text="Add New Admin",
                               font=self.title_font, bg="#f0f8ff", fg="#2a52be")
        title_label.pack(pady=(0, 30))

        # Form frame
        form_frame = tk.Frame(add_frame, bg="#f0f8ff")
        form_frame.pack(pady=20)

        # Entry styling
        entry_style = {
            "font": self.entry_font,
            "bg": "white",
            "relief": tk.SUNKEN,
            "borderwidth": 2
        }

        labels = ["Admin ID:", "Password:"]
        self.admin_entries = []

        for i, label in enumerate(labels):
            tk.Label(form_frame, text=label, font=self.label_font,
                     bg="#f0f8ff").grid(row=i, column=0, padx=10, pady=10, sticky="e")
            entry = tk.Entry(form_frame, **entry_style)
            entry.grid(row=i, column=1, padx=10, pady=10, ipady=5)
            self.admin_entries.append(entry)

        # Button frame
        button_frame = tk.Frame(add_frame, bg="#f0f8ff")
        button_frame.pack(pady=20)

        # Button styling
        btn_style = {
            "width": 15,
            "font": self.button_font,
            "bg": "#4682b4",
            "fg": "white",
            "activebackground": "#5f9ea0",
            "relief": tk.RAISED,
            "borderwidth": 3
        }

        submit_btn = tk.Button(button_frame, text="Submit",
                               command=self.submit_admin, **btn_style)
        submit_btn.grid(row=0, column=0, padx=15)

        back_btn = tk.Button(button_frame, text="Back",
                             command=self.admin_management, **btn_style)
        back_btn.grid(row=0, column=1, padx=15)

    def submit_admin(self):
        admin_id = self.admin_entries[0].get()
        password = self.admin_entries[1].get()

        if not all([admin_id, password]):
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            self.mycursor.execute("INSERT INTO AdminRecord VALUES (%s, %s)",
                                  (admin_id, password))
            self.mydb.commit()
            messagebox.showinfo("Success", "Admin added successfully!")
            self.admin_management()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Failed to add admin: {err}")

    def display_admins(self):
        self.clear_frame()

        # Main container
        display_frame = tk.Frame(self.root, bg="#f0f8ff")
        display_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Title
        title_label = tk.Label(display_frame, text="Admin Records",
                               font=self.title_font, bg="#f0f8ff", fg="#2a52be")
        title_label.pack(pady=(0, 20))

        # Treeview frame
        tree_frame = tk.Frame(display_frame, bg="#f0f8ff")
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Create Treeview
        tree = ttk.Treeview(tree_frame, columns=("ID", "Password"), show="headings")

        # Define headings
        tree.heading("ID", text="Admin ID")
        tree.heading("Password", text="Password")

        # Set column widths
        tree.column("ID", width=150, anchor="w")
        tree.column("Password", width=150, anchor="center")

        # Add striped row coloring
        tree.tag_configure('oddrow', background="#e6f2ff")
        tree.tag_configure('evenrow', background="#f0f8ff")

        # Get data from database
        self.mycursor.execute("SELECT * FROM AdminRecord")
        admins = self.mycursor.fetchall()

        # Insert data into treeview with alternating colors
        for i, admin in enumerate(admins):
            if i % 2 == 0:
                tree.insert("", "end", values=admin, tags=('evenrow',))
            else:
                tree.insert("", "end", values=admin, tags=('oddrow',))

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(fill="both", expand=True)

        # Button frame
        button_frame = tk.Frame(display_frame, bg="#f0f8ff")
        button_frame.pack(pady=20)

        # Button styling
        btn_style = {
            "width": 15,
            "font": self.button_font,
            "bg": "#4682b4",
            "fg": "white",
            "activebackground": "#5f9ea0",
            "relief": tk.RAISED,
            "borderwidth": 3
        }

        back_btn = tk.Button(button_frame, text="Back",
                             command=self.admin_management, **btn_style)
        back_btn.pack()

    def search_admin(self):
        admin_id = simpledialog.askstring("Search Admin", "Enter Admin ID:", parent=self.root)
        if not admin_id:
            return

        self.mycursor.execute("SELECT * FROM AdminRecord WHERE AdminID=%s", (admin_id,))
        admin = self.mycursor.fetchone()

        if admin:
            result_window = tk.Toplevel(self.root)
            result_window.title("Admin Details")
            result_window.configure(bg="#f0f8ff")
            result_window.geometry("400x200")

            # Title
            tk.Label(result_window, text="Admin Details",
                     font=self.title_font, bg="#f0f8ff", fg="#2a52be").pack(pady=(10, 20))

            # Details frame
            details_frame = tk.Frame(result_window, bg="#f0f8ff")
            details_frame.pack(pady=10, padx=20)

            labels = ["Admin ID:", "Password:"]

            for i, (label, value) in enumerate(zip(labels, admin)):
                tk.Label(details_frame, text=label, font=self.label_font,
                         bg="#f0f8ff", fg="#4682b4").grid(row=i, column=0, padx=10, pady=5, sticky="e")
                tk.Label(details_frame, text=value,
                         font=self.label_font, bg="#f0f8ff").grid(row=i, column=1, padx=10, pady=5, sticky="w")
        else:
            messagebox.showerror("Error", "Admin not found!")

    def delete_admin(self):
        admin_id = simpledialog.askstring("Delete Admin", "Enter Admin ID to delete:", parent=self.root)
        if not admin_id:
            return

        try:
            self.mycursor.execute("DELETE FROM AdminRecord WHERE AdminID=%s", (admin_id,))
            if self.mycursor.rowcount > 0:
                self.mydb.commit()
                messagebox.showinfo("Success", "Admin deleted successfully!")
            else:
                messagebox.showerror("Error", "Admin not found!")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Failed to delete admin: {err}")

    def update_admin(self):
        admin_id = simpledialog.askstring("Update Admin", "Enter Admin ID to update:", parent=self.root)
        if not admin_id:
            return

        # Check if admin exists
        self.mycursor.execute("SELECT * FROM AdminRecord WHERE AdminID=%s", (admin_id,))
        admin = self.mycursor.fetchone()

        if not admin:
            messagebox.showerror("Error", "Admin not found!")
            return

        # Create update window
        update_window = tk.Toplevel(self.root)
        update_window.title("Update Admin")
        update_window.configure(bg="#f0f8ff")
        update_window.geometry("400x200")

        # Title
        tk.Label(update_window, text="Update Admin Password",
                 font=self.title_font, bg="#f0f8ff", fg="#2a52be").pack(pady=(10, 20))

        # Form frame
        form_frame = tk.Frame(update_window, bg="#f0f8ff")
        form_frame.pack(pady=10, padx=20)

        # Entry styling
        entry_style = {
            "font": self.entry_font,
            "bg": "white",
            "relief": tk.SUNKEN,
            "borderwidth": 2
        }

        tk.Label(form_frame, text="New Password:", font=self.label_font,
                 bg="#f0f8ff").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        password_entry = tk.Entry(form_frame, **entry_style)
        password_entry.grid(row=0, column=1, padx=10, pady=10, ipady=5)

        # Button frame
        button_frame = tk.Frame(update_window, bg="#f0f8ff")
        button_frame.pack(pady=20)

        # Button styling
        btn_style = {
            "width": 15,
            "font": self.button_font,
            "bg": "#4682b4",
            "fg": "white",
            "activebackground": "#5f9ea0",
            "relief": tk.RAISED,
            "borderwidth": 3
        }

        def submit_update():
            new_password = password_entry.get()
            if not new_password:
                messagebox.showerror("Error", "Password is required!")
                return

            try:
                self.mycursor.execute("UPDATE AdminRecord SET Password=%s WHERE AdminID=%s",
                                      (new_password, admin_id))
                self.mydb.commit()
                messagebox.showinfo("Success", "Admin updated successfully!")
                update_window.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Failed to update admin: {err}")

        submit_btn = tk.Button(button_frame, text="Submit", command=submit_update, **btn_style)
        submit_btn.pack()

    def view_feedback(self):
        self.clear_frame()

        # Main container
        display_frame = tk.Frame(self.root, bg="#f0f8ff")
        display_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Title
        title_label = tk.Label(display_frame, text="Feedback and Ratings",
                               font=self.title_font, bg="#f0f8ff", fg="#2a52be")
        title_label.pack(pady=(0, 20))

        # Treeview frame
        tree_frame = tk.Frame(display_frame, bg="#f0f8ff")
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Create Treeview
        tree = ttk.Treeview(tree_frame, columns=("User", "Feedback", "Rating"), show="headings")

        # Define headings
        tree.heading("User", text="User ID")
        tree.heading("Feedback", text="Feedback")
        tree.heading("Rating", text="Rating (out of 10)")

        # Set column widths
        tree.column("User", width=100, anchor="center")
        tree.column("Feedback", width=400, anchor="w")
        tree.column("Rating", width=100, anchor="center")

        # Add striped row coloring
        tree.tag_configure('oddrow', background="#e6f2ff")
        tree.tag_configure('evenrow', background="#f0f8ff")

        # Get data from database
        self.mycursor.execute("""SELECT Feedback.UserID, Feedback.Feedback, Feedback.Rating
                                FROM Feedback
                                JOIN UserRecord ON Feedback.UserID=UserRecord.UserID""")
        feedbacks = self.mycursor.fetchall()

        # Insert data into treeview with alternating colors
        for i, feedback in enumerate(feedbacks):
            if i % 2 == 0:
                tree.insert("", "end", values=feedback, tags=('evenrow',))
            else:
                tree.insert("", "end", values=feedback, tags=('oddrow',))

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(fill="both", expand=True)

        # Button frame
        button_frame = tk.Frame(display_frame, bg="#f0f8ff")
        button_frame.pack(pady=20)

        # Button styling
        btn_style = {
            "width": 15,
            "font": self.button_font,
            "bg": "#4682b4",
            "fg": "white",
            "activebackground": "#5f9ea0",
            "relief": tk.RAISED,
            "borderwidth": 3
        }

        back_btn = tk.Button(button_frame, text="Back",
                             command=self.admin_menu, **btn_style)
        back_btn.pack()

    def user_login(self, attempts=0):
        self.clear_frame()

        if attempts >= 3:
            messagebox.showerror("Error", "Too many failed attempts. System will now exit.")
            self.root.quit()
            return

        # Main container
        login_frame = tk.Frame(self.root, bg="#f0f8ff")
        login_frame.pack(expand=True, fill="both", padx=100, pady=50)

        # Title
        title_label = tk.Label(login_frame, text="User Login / Register",
                               font=self.title_font, bg="#f0f8ff", fg="#2a52be")
        title_label.pack(pady=(0, 30))

        # Button frame
        button_frame = tk.Frame(login_frame, bg="#f0f8ff")
        button_frame.pack(pady=40)

        # Button styling
        btn_style = {
            "width": 20,
            "height": 2,
            "font": self.button_font,
            "bg": "#4682b4",
            "fg": "white",
            "activebackground": "#5f9ea0",
            "relief": tk.RAISED,
            "borderwidth": 3
        }

        login_btn = tk.Button(button_frame, text="Login",
                              command=lambda: self.show_user_login(attempts), **btn_style)
        login_btn.grid(row=0, column=0, padx=15, pady=15, ipadx=10)

        register_btn = tk.Button(button_frame, text="Register",
                                 command=self.register_user, **btn_style)
        register_btn.grid(row=0, column=1, padx=15, pady=15, ipadx=10)

        back_btn = tk.Button(button_frame, text="Back",
                             command=self.create_main_menu, **btn_style)
        back_btn.grid(row=1, column=0, columnspan=2, pady=15, ipadx=10)

    def show_user_login(self, attempts):
        self.clear_frame()

        # Main container
        login_frame = tk.Frame(self.root, bg="#f0f8ff")
        login_frame.pack(expand=True, fill="both", padx=100, pady=50)

        # Title
        title_label = tk.Label(login_frame, text="User Login",
                               font=self.title_font, bg="#f0f8ff", fg="#2a52be")
        title_label.pack(pady=(0, 30))

        # Form frame
        form_frame = tk.Frame(login_frame, bg="#f0f8ff")
        form_frame.pack(pady=20)

        # Entry styling
        entry_style = {
            "font": self.entry_font,
            "bg": "white",
            "relief": tk.SUNKEN,
            "borderwidth": 2
        }

        # Labels and entries
        tk.Label(form_frame, text="User ID:", font=self.label_font,
                 bg="#f0f8ff").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.user_id_entry = tk.Entry(form_frame, **entry_style)
        self.user_id_entry.grid(row=0, column=1, padx=10, pady=10, ipady=5)

        tk.Label(form_frame, text="Password:", font=self.label_font,
                 bg="#f0f8ff").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.user_pass_entry = tk.Entry(form_frame, show="*", **entry_style)
        self.user_pass_entry.grid(row=1, column=1, padx=10, pady=10, ipady=5)

        # Button frame
        button_frame = tk.Frame(login_frame, bg="#f0f8ff")
        button_frame.pack(pady=20)

        # Button styling
        btn_style = {
            "width": 15,
            "font": self.button_font,
            "bg": "#4682b4",
            "fg": "white",
            "activebackground": "#5f9ea0",
            "relief": tk.RAISED,
            "borderwidth": 3
        }

        login_btn = tk.Button(button_frame, text="Login",
                              command=lambda: self.verify_user_login(attempts), **btn_style)
        login_btn.grid(row=0, column=0, padx=15)

        back_btn = tk.Button(button_frame, text="Back",
                             command=lambda: self.user_login(attempts), **btn_style)
        back_btn.grid(row=0, column=1, padx=15)

    def verify_user_login(self, attempts):
        user_id = self.user_id_entry.get()
        password = self.user_pass_entry.get()

        self.mycursor.execute("SELECT Password FROM UserRecord WHERE UserID=%s", (user_id,))
        result = self.mycursor.fetchone()

        if result:
            if result[0] == password:
                messagebox.showinfo("Success", f"Welcome {user_id} to THE BOOK HUB")
                self.current_user = user_id
                self.user_menu()
            else:
                messagebox.showerror("Error", "Invalid password!")
                self.user_login(attempts + 1)
        else:
            messagebox.showerror("Error", "No such user ID exists!")
            self.user_login(attempts + 1)

    def register_user(self):
        self.clear_frame()

        # Main container
        register_frame = tk.Frame(self.root, bg="#f0f8ff")
        register_frame.pack(expand=True, fill="both", padx=100, pady=50)

        # Title
        title_label = tk.Label(register_frame, text="Register New User",
                               font=self.title_font, bg="#f0f8ff", fg="#2a52be")
        title_label.pack(pady=(0, 30))

        # Form frame
        form_frame = tk.Frame(register_frame, bg="#f0f8ff")
        form_frame.pack(pady=20)

        # Entry styling
        entry_style = {
            "font": self.entry_font,
            "bg": "white",
            "relief": tk.SUNKEN,
            "borderwidth": 2
        }

        labels = ["User ID:", "User Name:", "Password:"]
        self.register_entries = []

        for i, label in enumerate(labels):
            tk.Label(form_frame, text=label, font=self.label_font,
                     bg="#f0f8ff").grid(row=i, column=0, padx=10, pady=10, sticky="e")
            entry = tk.Entry(form_frame, **entry_style)
            entry.grid(row=i, column=1, padx=10, pady=10, ipady=5)
            self.register_entries.append(entry)

        # Button frame
        button_frame = tk.Frame(register_frame, bg="#f0f8ff")
        button_frame.pack(pady=20)

        # Button styling
        btn_style = {
            "width": 15,
            "font": self.button_font,
            "bg": "#4682b4",
            "fg": "white",
            "activebackground": "#5f9ea0",
            "relief": tk.RAISED,
            "borderwidth": 3
        }

        submit_btn = tk.Button(button_frame, text="Submit",
                               command=self.submit_registration, **btn_style)
        submit_btn.grid(row=0, column=0, padx=15)

        back_btn = tk.Button(button_frame, text="Back",
                             command=lambda: self.user_login(0), **btn_style)
        back_btn.grid(row=0, column=1, padx=15)

    def submit_registration(self):
        user_id = self.register_entries[0].get()
        user_name = self.register_entries[1].get()
        password = self.register_entries[2].get()

        if not all([user_id, user_name, password]):
            messagebox.showerror("Error", "All fields are required!")
            return

        # Check if user already exists
        self.mycursor.execute("SELECT UserID FROM UserRecord WHERE UserID=%s", (user_id,))
        if self.mycursor.fetchone():
            messagebox.showerror("Error", "User ID already exists!")
            return

        try:
            self.mycursor.execute("INSERT INTO UserRecord (UserID, UserName, Password, BookID) VALUES (%s, %s, %s, %s)",
                                  (user_id, user_name, password, None))
            self.mydb.commit()
            messagebox.showinfo("Success", "Registration successful! Please login.")
            self.user_login(0)
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Failed to register: {err}")

    def user_menu(self):
        self.clear_frame()

        # Main container
        menu_frame = tk.Frame(self.root, bg="#f0f8ff")
        menu_frame.pack(expand=True, fill="both", padx=50, pady=50)

        # Title
        title_label = tk.Label(menu_frame, text=f"Welcome, User {self.current_user}",
                               font=self.title_font, bg="#f0f8ff", fg="#2a52be")
        title_label.pack(pady=(0, 30))

        # Button frame
        button_frame = tk.Frame(menu_frame, bg="#f0f8ff")
        button_frame.pack(pady=20)

        # Button styling
        btn_style = {
            "width": 20,
            "height": 2,
            "font": self.button_font,
            "bg": "#4682b4",
            "fg": "white",
            "activebackground": "#5f9ea0",
            "relief": tk.RAISED,
            "borderwidth": 3
        }

        buttons = [
            ("Book Center", self.user_book_center),
            ("Give Feedback", self.user_feedback),
            ("Logout", self.create_main_menu)
        ]

        for i, (text, command) in enumerate(buttons):
            btn = tk.Button(button_frame, text=text, command=command, **btn_style)
            btn.grid(row=i, column=0, padx=15, pady=15, ipadx=10)

    def user_book_center(self):
        self.clear_frame()

        # Main container
        menu_frame = tk.Frame(self.root, bg="#f0f8ff")
        menu_frame.pack(expand=True, fill="both", padx=50, pady=50)

        # Title
        title_label = tk.Label(menu_frame, text="Book Center",
                               font=self.title_font, bg="#f0f8ff", fg="#2a52be")
        title_label.pack(pady=(0, 30))

        # Button frame
        button_frame = tk.Frame(menu_frame, bg="#f0f8ff")
        button_frame.pack(pady=20)

        # Button styling
        btn_style = {
            "width": 20,
            "height": 2,
            "font": self.button_font,
            "bg": "#4682b4",
            "fg": "white",
            "activebackground": "#5f9ea0",
            "relief": tk.RAISED,
            "borderwidth": 3
        }

        buttons = [
            ("List All Books", self.user_list_books),
            ("Issue Book", self.user_issue_book),
            ("View Issued Book", self.user_view_issued_book),
            ("Return Book", self.user_return_book),
            ("Get Recommendations", self.user_recommendations),
            ("Back", self.user_menu)
        ]

        for i, (text, command) in enumerate(buttons):
            btn = tk.Button(button_frame, text=text, command=command, **btn_style)
            btn.grid(row=i // 2, column=i % 2, padx=15, pady=15, ipadx=10)

    def user_list_books(self):
        self.clear_frame()

        # Main container
        display_frame = tk.Frame(self.root, bg="#f0f8ff")
        display_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Title
        title_label = tk.Label(display_frame, text="Available Books",
                               font=self.title_font, bg="#f0f8ff", fg="#2a52be")
        title_label.pack(pady=(0, 20))

        # Treeview frame
        tree_frame = tk.Frame(display_frame, bg="#f0f8ff")
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Create Treeview
        tree = ttk.Treeview(tree_frame, columns=("ID", "Name", "Author", "Publisher", "Genre"), show="headings")

        # Define headings
        tree.heading("ID", text="Book ID")
        tree.heading("Name", text="Book Name")
        tree.heading("Author", text="Author")
        tree.heading("Publisher", text="Publisher")
        tree.heading("Genre", text="Genre")

        # Set column widths
        tree.column("ID", width=100, anchor="center")
        tree.column("Name", width=200, anchor="w")
        tree.column("Author", width=150, anchor="w")
        tree.column("Publisher", width=150, anchor="w")
        tree.column("Genre", width=100, anchor="w")

        # Add striped row coloring
        tree.tag_configure('oddrow', background="#e6f2ff")
        tree.tag_configure('evenrow', background="#f0f8ff")

        # Get available books (not issued to anyone)
        self.mycursor.execute("""SELECT BookID, BookName, Author, Publisher, Genre 
                                FROM BookRecord 
                                WHERE BookID NOT IN (
                                    SELECT BookID FROM UserRecord WHERE BookID IS NOT NULL
                                )""")
        books = self.mycursor.fetchall()

        # Insert data into treeview with alternating colors
        for i, book in enumerate(books):
            if i % 2 == 0:
                tree.insert("", "end", values=book, tags=('evenrow',))
            else:
                tree.insert("", "end", values=book, tags=('oddrow',))

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(fill="both", expand=True)

        # Button frame
        button_frame = tk.Frame(display_frame, bg="#f0f8ff")
        button_frame.pack(pady=20)

        # Button styling
        btn_style = {
            "width": 15,
            "font": self.button_font,
            "bg": "#4682b4",
            "fg": "white",
            "activebackground": "#5f9ea0",
            "relief": tk.RAISED,
            "borderwidth": 3
        }

        back_btn = tk.Button(button_frame, text="Back",
                             command=self.user_book_center, **btn_style)
        back_btn.pack()

    def user_issue_book(self):
        book_id = simpledialog.askstring("Issue Book", "Enter Book ID to issue:", parent=self.root)
        if not book_id:
            return

        # Check if book is available
        self.mycursor.execute("SELECT BookID, Genre FROM BookRecord WHERE BookID=%s", (book_id,))
        book_data = self.mycursor.fetchone()
        if not book_data:
            messagebox.showerror("Error", "Book not found!")
            return

        book_id, genre = book_data

        # Check if book is already issued
        self.mycursor.execute("SELECT BookID FROM UserRecord WHERE BookID=%s", (book_id,))
        if self.mycursor.fetchone():
            messagebox.showerror("Error", "Book is already issued to someone else!")
            return

        # Check if user already has a book issued
        self.mycursor.execute("SELECT BookID FROM UserRecord WHERE UserID=%s", (self.current_user,))
        result = self.mycursor.fetchone()
        if result and result[0]:
            messagebox.showerror("Error", "You already have a book issued. Return it first.")
            return

        try:
            # Issue the book
            self.mycursor.execute("UPDATE UserRecord SET BookID=%s WHERE UserID=%s",
                                  (book_id, self.current_user))

            # Record in reading history
            self.mycursor.execute("INSERT INTO UserReadingHistory (UserID, BookID, Genre) VALUES (%s, %s, %s)",
                                  (self.current_user, book_id, genre))

            self.mydb.commit()
            messagebox.showinfo("Success", "Book issued successfully!")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Failed to issue book: {err}")

    def user_view_issued_book(self):
        self.clear_frame()

        # Main container
        display_frame = tk.Frame(self.root, bg="#f0f8ff")
        display_frame.pack(expand=True, fill="both", padx=50, pady=50)

        # Title
        title_label = tk.Label(display_frame, text="Your Issued Book",
                               font=self.title_font, bg="#f0f8ff", fg="#2a52be")
        title_label.pack(pady=(0, 30))

        # Get issued book details
        self.mycursor.execute("""SELECT BookRecord.BookID, BookRecord.BookName, 
                                BookRecord.Author, BookRecord.Publisher, BookRecord.Genre
                                FROM BookRecord
                                INNER JOIN UserRecord ON BookRecord.BookID=UserRecord.BookID
                                WHERE UserRecord.UserID=%s""", (self.current_user,))
        book = self.mycursor.fetchone()

        if book:
            details_frame = tk.Frame(display_frame, bg="#f0f8ff")
            details_frame.pack(pady=20)

            labels = ["Book ID:", "Book Name:", "Author:", "Publisher:", "Genre:"]

            for i, (label, value) in enumerate(zip(labels, book)):
                tk.Label(details_frame, text=label, font=self.label_font,
                         bg="#f0f8ff", fg="#4682b4").grid(row=i, column=0, padx=10, pady=10, sticky="e")
                tk.Label(details_frame, text=value,
                         font=self.label_font, bg="#f0f8ff").grid(row=i, column=1, padx=10, pady=10, sticky="w")
        else:
            tk.Label(display_frame, text="You don't have any books issued.",
                     font=self.label_font, bg="#f0f8ff").pack(pady=20)

        # Button frame
        button_frame = tk.Frame(display_frame, bg="#f0f8ff")
        button_frame.pack(pady=20)

        # Button styling
        btn_style = {
            "width": 15,
            "font": self.button_font,
            "bg": "#4682b4",
            "fg": "white",
            "activebackground": "#5f9ea0",
            "relief": tk.RAISED,
            "borderwidth": 3
        }

        back_btn = tk.Button(button_frame, text="Back",
                             command=self.user_book_center, **btn_style)
        back_btn.pack()

    def user_return_book(self):
        # Check if user has a book issued
        self.mycursor.execute("SELECT BookID FROM UserRecord WHERE UserID=%s", (self.current_user,))
        result = self.mycursor.fetchone()

        if not result or not result[0]:
            messagebox.showerror("Error", "You don't have any books to return!")
            return

        try:
            self.mycursor.execute("UPDATE UserRecord SET BookID=NULL WHERE UserID=%s",
                                  (self.current_user,))
            self.mydb.commit()
            messagebox.showinfo("Success", "Book returned successfully!")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Failed to return book: {err}")

    def user_recommendations(self):
        # Get user's reading history to find favorite genres
        self.mycursor.execute("SELECT Genre FROM UserReadingHistory WHERE UserID=%s", (self.current_user,))
        genres = [row[0] for row in self.mycursor.fetchall()]

        if not genres:
            messagebox.showinfo("Info",
                                "We don't have enough data to make recommendations. Please issue some books first.")
            return

        # Count genre occurrences
        genre_counts = defaultdict(int)
        for genre in genres:
            genre_counts[genre] += 1

        # Get top 2 genres
        top_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:2]
        top_genres = [genre for genre, count in top_genres]

        # Get recommended books in these genres that the user hasn't read
        query = """SELECT BookID, BookName, Author, Publisher, Genre 
                   FROM BookRecord 
                   WHERE Genre IN (%s, %s) 
                   AND BookID NOT IN (
                       SELECT BookID FROM UserReadingHistory WHERE UserID=%s
                   )
                   AND BookID NOT IN (
                       SELECT BookID FROM UserRecord WHERE BookID IS NOT NULL
                   )
                   LIMIT 10"""

        self.mycursor.execute(query, (
        top_genres[0], top_genres[1] if len(top_genres) > 1 else top_genres[0], self.current_user))
        recommended_books = self.mycursor.fetchall()

        if not recommended_books:
            messagebox.showinfo("Info", "No recommendations available based on your reading history.")
            return

        # Display recommendations
        self.clear_frame()

        # Main container
        display_frame = tk.Frame(self.root, bg="#f0f8ff")
        display_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Title
        title_label = tk.Label(display_frame, text="Recommended Books For You",
                               font=self.title_font, bg="#f0f8ff", fg="#2a52be")
        title_label.pack(pady=(0, 20))

        # Subtitle with favorite genres
        subtitle = f"Based on your interest in: {', '.join(top_genres)}"
        subtitle_label = tk.Label(display_frame, text=subtitle,
                                  font=self.subtitle_font, bg="#f0f8ff", fg="#4682b4")
        subtitle_label.pack(pady=(0, 20))

        # Treeview frame
        tree_frame = tk.Frame(display_frame, bg="#f0f8ff")
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Create Treeview
        tree = ttk.Treeview(tree_frame, columns=("ID", "Name", "Author", "Publisher", "Genre"), show="headings")

        # Define headings
        tree.heading("ID", text="Book ID")
        tree.heading("Name", text="Book Name")
        tree.heading("Author", text="Author")
        tree.heading("Publisher", text="Publisher")
        tree.heading("Genre", text="Genre")

        # Set column widths
        tree.column("ID", width=100, anchor="center")
        tree.column("Name", width=200, anchor="w")
        tree.column("Author", width=150, anchor="w")
        tree.column("Publisher", width=150, anchor="w")
        tree.column("Genre", width=100, anchor="w")

        # Add striped row coloring
        tree.tag_configure('oddrow', background="#e6f2ff")
        tree.tag_configure('evenrow', background="#f0f8ff")

        # Insert recommended books
        for i, book in enumerate(recommended_books):
            if i % 2 == 0:
                tree.insert("", "end", values=book, tags=('evenrow',))
            else:
                tree.insert("", "end", values=book, tags=('oddrow',))

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(fill="both", expand=True)

        # Button frame
        button_frame = tk.Frame(display_frame, bg="#f0f8ff")
        button_frame.pack(pady=20)

        # Button styling
        btn_style = {
            "width": 15,
            "font": self.button_font,
            "bg": "#4682b4",
            "fg": "white",
            "activebackground": "#5f9ea0",
            "relief": tk.RAISED,
            "borderwidth": 3
        }

        issue_btn = tk.Button(button_frame, text="Issue Selected",
                              command=lambda: self.issue_selected_book(tree), **btn_style)
        issue_btn.pack(side="left", padx=10)

        back_btn = tk.Button(button_frame, text="Back",
                             command=self.user_book_center, **btn_style)
        back_btn.pack(side="right", padx=10)

    def issue_selected_book(self, tree):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a book to issue!")
            return

        book_id = tree.item(selected_item)['values'][0]
        self.user_issue_book_with_id(book_id)

    def user_issue_book_with_id(self, book_id):
        # Check if book is available
        self.mycursor.execute("SELECT BookID, Genre FROM BookRecord WHERE BookID=%s", (book_id,))
        book_data = self.mycursor.fetchone()
        if not book_data:
            messagebox.showerror("Error", "Book not found!")
            return

        book_id, genre = book_data

        # Check if book is already issued
        self.mycursor.execute("SELECT BookID FROM UserRecord WHERE BookID=%s", (book_id,))
        if self.mycursor.fetchone():
            messagebox.showerror("Error", "Book is already issued to someone else!")
            return

        # Check if user already has a book issued
        self.mycursor.execute("SELECT BookID FROM UserRecord WHERE UserID=%s", (self.current_user,))
        result = self.mycursor.fetchone()
        if result and result[0]:
            messagebox.showerror("Error", "You already have a book issued. Return it first.")
            return

        try:
            # Issue the book
            self.mycursor.execute("UPDATE UserRecord SET BookID=%s WHERE UserID=%s",
                                  (book_id, self.current_user))

            # Record in reading history
            self.mycursor.execute("INSERT INTO UserReadingHistory (UserID, BookID, Genre) VALUES (%s, %s, %s)",
                                  (self.current_user, book_id, genre))

            self.mydb.commit()
            messagebox.showinfo("Success", "Book issued successfully!")
            self.user_book_center()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Failed to issue book: {err}")

    def user_feedback(self):
        self.clear_frame()

        # Main container
        feedback_frame = tk.Frame(self.root, bg="#f0f8ff")
        feedback_frame.pack(expand=True, fill="both", padx=100, pady=50)

        # Title
        title_label = tk.Label(feedback_frame, text="Feedback and Rating",
                               font=self.title_font, bg="#f0f8ff", fg="#2a52be")
        title_label.pack(pady=(0, 30))

        # Form frame
        form_frame = tk.Frame(feedback_frame, bg="#f0f8ff")
        form_frame.pack(pady=20)

        # Text styling
        text_style = {
            "font": self.entry_font,
            "bg": "white",
            "relief": tk.SUNKEN,
            "borderwidth": 2,
            "wrap": tk.WORD
        }

        # Entry styling
        entry_style = {
            "font": self.entry_font,
            "bg": "white",
            "relief": tk.SUNKEN,
            "borderwidth": 2
        }

        tk.Label(form_frame, text="Your Feedback:", font=self.label_font,
                 bg="#f0f8ff").grid(row=0, column=0, padx=10, pady=5, sticky="ne")
        self.feedback_entry = tk.Text(form_frame, width=50, height=5, **text_style)
        self.feedback_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(form_frame, text="Rating (1-10):", font=self.label_font,
                 bg="#f0f8ff").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.rating_entry = tk.Entry(form_frame, **entry_style)
        self.rating_entry.grid(row=1, column=1, padx=10, pady=5, ipady=5)

        # Button frame
        button_frame = tk.Frame(feedback_frame, bg="#f0f8ff")
        button_frame.pack(pady=20)

        # Button styling
        btn_style = {
            "width": 15,
            "font": self.button_font,
            "bg": "#4682b4",
            "fg": "white",
            "activebackground": "#5f9ea0",
            "relief": tk.RAISED,
            "borderwidth": 3
        }

        submit_btn = tk.Button(button_frame, text="Submit",
                               command=self.submit_feedback, **btn_style)
        submit_btn.grid(row=0, column=0, padx=15)

        back_btn = tk.Button(button_frame, text="Back",
                             command=self.user_menu, **btn_style)
        back_btn.grid(row=0, column=1, padx=15)

    def submit_feedback(self):
        feedback = self.feedback_entry.get("1.0", "end-1c").strip()
        rating = self.rating_entry.get().strip()

        if not feedback:
            messagebox.showerror("Error", "Feedback cannot be empty!")
            return

        if not rating.isdigit() or int(rating) < 1 or int(rating) > 10:
            messagebox.showerror("Error", "Please enter a valid rating between 1 and 10")
            return

        try:
            self.mycursor.execute("INSERT INTO Feedback (UserID, Feedback, Rating) VALUES (%s, %s, %s)",
                                  (self.current_user, feedback, rating))
            self.mydb.commit()
            messagebox.showinfo("Success", "Thank you for your feedback!")
            self.user_menu()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Failed to submit feedback: {err}")


if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryManagementSystem(root)
    root.mainloop()