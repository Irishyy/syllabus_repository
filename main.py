import tkinter as tk
from tkinter import messagebox
from auth import verify_login
from database import init_database
from app import SyllabusApp

class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Syllabus Manager - Login")
        self.root.geometry("400x250")
        self.root.resizable(False, False)

        # Center window
        self.center_window(400, 250)

        # Initialize database
        init_database()

        # Create UI
        self.create_widgets()

    def center_window(self, width, height):
        """Centers the window on the screen."""
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        # Header
        header = tk.Label(
            self.root,
            text="Syllabus Repository System",
            font=("Arial", 16, "bold"),
            fg="#2c3e50"
        )
        header.pack(pady=20)

        # Login frame
        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        # Username
        tk.Label(frame, text="Username:", font=("Arial", 11)).grid(row=0, column=0, sticky="e", padx=10, pady=10)
        self.username_entry = tk.Entry(frame, font=("Arial", 11), width=20)
        self.username_entry.grid(row=0, column=1, pady=10)
        self.username_entry.insert(0, "admin")

        # Password
        tk.Label(frame, text="Password:", font=("Arial", 11)).grid(row=1, column=0, sticky="e", padx=10, pady=10)
        self.password_entry = tk.Entry(frame, font=("Arial", 11), width=20, show="●")
        self.password_entry.grid(row=1, column=1, pady=10)

        # Login button
        login_btn = tk.Button(
            self.root,
            text="Login",
            font=("Arial", 12, "bold"),
            bg="#3498db",
            fg="white",
            width=15,
            cursor="hand2",
            command=self.login
        )
        login_btn.pack(pady=15)

        # Info label
        info = tk.Label(
            self.root,
            text="Default: admin / 1234",
            font=("Arial", 9),
            fg="gray"
        )
        info.pack()

        # Bind Enter key
        self.root.bind('<Return>', lambda e: self.login())
        self.username_entry.focus()

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter both username and password")
            return

        if verify_login(username, password):
            self.root.destroy()
            # Launch main app
            app = SyllabusApp()
            app.mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus()

    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    login = LoginWindow()
    login.run()