import tkinter as tk
from tkinter import messagebox
import sqlite3
import os

class PipoBookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PipoBook")
        self.root.geometry("400x300")

        self.label = tk.Label(root, text="PipoBook", font=("Arial", 24))
        self.label.pack(pady=20)

        self.btn_register = tk.Button(root, text="Registrarse", font=("Arial", 12), command=self.register)
        self.btn_register.pack(pady=5)

        self.btn_login = tk.Button(root, text="Iniciar Sesión", font=("Arial", 12), command=self.login)
        self.btn_login.pack(pady=5)

        self.db_connection = sqlite3.connect('pipo_book.db')
        self.cursor = self.db_connection.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users
                            (id INTEGER PRIMARY KEY,
                             name TEXT NOT NULL,
                             password TEXT NOT NULL)''')
        self.db_connection.commit()

    def register(self):
        register_window = tk.Toplevel(self.root)
        register_window.title("Registro")
        register_window.geometry("400x300")

        tk.Label(register_window, text="Nombre:").pack()
        name_entry = tk.Entry(register_window)
        name_entry.pack()

        tk.Label(register_window, text="Contraseña:").pack()
        password_entry = tk.Entry(register_window, show="*")
        password_entry.pack()

        tk.Label(register_window, text="Verificar Contraseña:").pack()
        verify_password_entry = tk.Entry(register_window, show="*")
        verify_password_entry.pack()

        def register_user():
            name = name_entry.get()
            password = password_entry.get()
            verify_password = verify_password_entry.get()

            if not (name and password and verify_password):
                messagebox.showerror("Error", "Por favor complete todos los campos.")
                return

            if password != verify_password:
                messagebox.showerror("Error", "Las contraseñas no coinciden.")
                return

            self.check_existing_user(name)

            self.save_user(name, password)

            register_window.destroy()  # Cerrar la ventana de registro
            self.open_inicio()

        tk.Button(register_window, text="Registrarse", command=register_user).pack()

    def login(self):
        login_window = tk.Toplevel(self.root)
        login_window.title("Iniciar Sesión")
        login_window.geometry("300x150")

        tk.Label(login_window, text="Nombre:").pack()
        name_entry = tk.Entry(login_window)
        name_entry.pack()

        tk.Label(login_window, text="Contraseña:").pack()
        password_entry = tk.Entry(login_window, show="*")
        password_entry.pack()

        def login_user():
            name = name_entry.get()
            password = password_entry.get()

            if not (name and password):
                messagebox.showerror("Error", "Por favor complete todos los campos.")
                return

            if self.check_credentials(name, password):
                messagebox.showinfo("Inicio de sesión exitoso", "¡Bienvenido a PipoBook!")
                login_window.destroy()  # Cerrar la ventana de inicio de sesión
                self.open_inicio()
            else:
                messagebox.showerror("Error", "Credenciales incorrectas.")

        tk.Button(login_window, text="Iniciar Sesión", command=login_user).pack()

    def check_credentials(self, name, password):
        self.cursor.execute("SELECT * FROM users WHERE name=? AND password=?", (name, password))
        return self.cursor.fetchone()

    def check_existing_user(self, name):
        self.cursor.execute("SELECT * FROM users WHERE name=?", (name,))
        if self.cursor.fetchone():
            messagebox.showerror("Error", "Usuario ya existente")

    def save_user(self, name, password):
        self.cursor.execute("INSERT INTO users (name, password) VALUES (?, ?)", (name, password))
        self.db_connection.commit()

    def open_inicio(self):
        os.system('python PipoBook.py')  # Ejecutar Inicio.py

root = tk.Tk()
app = PipoBookApp(root)
root.mainloop()
