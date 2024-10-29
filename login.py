import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
import sqlite3
import hashlib
from main import FinanceDashboard  # Import the main dashboard class

class LoginPage(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Login Page")
        self.geometry("400x300")
        self.style = tb.Style("lumen")

        self.mainFrame = ttk.Frame(self, padding="10")
        self.mainFrame.pack(expand=True, fill=tk.BOTH)

        self.emailLabel = ttk.Label(self.mainFrame, text="Email:")
        self.emailLabel.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.emailEntry = ttk.Entry(self.mainFrame)
        self.emailEntry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.passwordLabel = ttk.Label(self.mainFrame, text="Password:")
        self.passwordLabel.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.passwordEntry = ttk.Entry(self.mainFrame, show='*')
        self.passwordEntry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.loginButton = ttk.Button(self.mainFrame, text="Login", command=self.login)
        self.loginButton.grid(row=2, column=0, columnspan=2, pady=10)

        self.registerButton = ttk.Button(self.mainFrame, text="Register", command=self.register)
        self.registerButton.grid(row=3, column=0, columnspan=2)

        self.mainFrame.columnconfigure(1, weight=1)

    def login(self):
        email = self.emailEntry.get()
        password = self.passwordEntry.get()
        hashedPassword = hashlib.sha256(password.encode()).hexdigest()

        conn = sqlite3.connect('finance.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, hashedPassword))
        user = c.fetchone()
        conn.close()

        if user:
            messagebox.showinfo("Login Success", "You have successfully logged in.")
            self.withdraw()
            self.openDashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid email or password.")

    def register(self):
        RegisterPage(self)

    def openDashboard(self):
        root = tk.Toplevel(self)
        app = FinanceDashboard(root)
        root.mainloop()

class RegisterPage(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Register Page")
        self.geometry("400x300")
        self.style = tb.Style("lumen")

        self.mainFrame = ttk.Frame(self, padding="10")
        self.mainFrame.pack(expand=True, fill=tk.BOTH)

        self.emailLabel = ttk.Label(self.mainFrame, text="Email:")
        self.emailLabel.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.emailEntry = ttk.Entry(self.mainFrame)
        self.emailEntry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.passwordLabel = ttk.Label(self.mainFrame, text="Password:")
        self.passwordLabel.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.passwordEntry = ttk.Entry(self.mainFrame, show='*')
        self.passwordEntry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.confirmPasswordLabel = ttk.Label(self.mainFrame, text="Confirm Password:")
        self.confirmPasswordLabel.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.confirmPasswordEntry = ttk.Entry(self.mainFrame, show='*')
        self.confirmPasswordEntry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        self.registerButton = ttk.Button(self.mainFrame, text="Register", command=self.register)
        self.registerButton.grid(row=3, column=0, columnspan=2, pady=10)

        self.mainFrame.columnconfigure(1, weight=1)

    def register(self):
        email = self.emailEntry.get()
        password = self.passwordEntry.get()
        confirmPassword = self.confirmPasswordEntry.get()

        if not email or not password:
            messagebox.showerror("Registration Failed", "Please fill all fields.")
            return

        if password != confirmPassword:
            messagebox.showerror("Registration Failed", "Passwords do not match.")
            return

        hashedPassword = hashlib.sha256(password.encode()).hexdigest()

        conn = sqlite3.connect('finance.db')
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, hashedPassword))
            conn.commit()
            messagebox.showinfo("Registration Success", "You have successfully registered.")
            self.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Registration Failed", "Email already registered.")
        finally:
            conn.close()

if __name__ == "__main__":
    app = LoginPage()
    app.mainloop()
