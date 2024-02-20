import tkinter as tk
from tkinter import messagebox, filedialog
import sqlite3
import os

class PipoBookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PipoBook")
        self.root.geometry("800x600")

        self.label = tk.Label(root, text="Bienvenido a PipoBook", font=("Arial", 18))
        self.label.pack(pady=20)

        self.account_button = tk.Button(root, text="Tu Cuenta", font=("Arial", 12), command=self.show_account)
        self.account_button.place(relx=0.05, rely=0.05, anchor="nw")

        self.post_button = tk.Button(root, text="Publicar", font=("Arial", 12), command=self.create_post)
        self.post_button.place(relx=0.95, rely=0.05, anchor="ne")

        self.friends_button = tk.Button(root, text="Amigos", font=("Arial", 12), command=self.show_friends)
        self.friends_button.place(relx=0.95, rely=0.15, anchor="ne")

        self.groups_button = tk.Button(root, text="Grupos", font=("Arial", 12), command=self.show_groups)
        self.groups_button.place(relx=0.95, rely=0.25, anchor="ne")

        self.messages_button = tk.Button(root, text="Mensajes", font=("Arial", 12), command=self.show_messages)
        self.messages_button.place(relx=0.95, rely=0.35, anchor="ne")

        self.profile_button = tk.Button(root, text="Perfil", font=("Arial", 12), command=self.show_profile)
        self.profile_button.place(relx=0.95, rely=0.45, anchor="ne")

        self.search_frame = tk.Frame(root)
        self.search_frame.place(relx=0.5, rely=0.05, relwidth=0.4, anchor="n")

        self.search_label = tk.Label(self.search_frame, text="Buscar Amigos:")
        self.search_label.grid(row=0, column=0, padx=5, pady=5)

        self.search_entry = tk.Entry(self.search_frame)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)

        self.search_button = tk.Button(self.search_frame, text="Buscar", command=self.search_friends)
        self.search_button.grid(row=0, column=2, padx=5, pady=5)

        self.posts_frame = tk.Frame(root)
        self.posts_frame.place(relx=0.5, rely=0.15, relwidth=0.9, relheight=0.7, anchor="n")

        self.scrollbar = tk.Scrollbar(self.posts_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.posts_list = tk.Listbox(self.posts_frame, yscrollcommand=self.scrollbar.set)
        self.posts_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar.config(command=self.posts_list.yview)

        self.db_connection = sqlite3.connect('pipo_book.db')
        self.cursor = self.db_connection.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS posts
                            (id INTEGER PRIMARY KEY,
                             text TEXT,
                             image TEXT,
                             likes INTEGER DEFAULT 0,
                             dislikes INTEGER DEFAULT 0)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS comments
                            (id INTEGER PRIMARY KEY,
                             post_id INTEGER,
                             commenter_id INTEGER,
                             comment_text TEXT,
                             likes INTEGER DEFAULT 0,
                             dislikes INTEGER DEFAULT 0)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS friends
                            (id INTEGER PRIMARY KEY,
                             name TEXT,
                             status TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS friend_requests
                            (id INTEGER PRIMARY KEY,
                             requester_id INTEGER,
                             receiver_id INTEGER,
                             status TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS messages
                            (id INTEGER PRIMARY KEY,
                             sender_id INTEGER,
                             receiver_id INTEGER,
                             message_text TEXT,
                             status TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS groups
                            (id INTEGER PRIMARY KEY,
                             name TEXT,
                             description TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS group_members
                            (id INTEGER PRIMARY KEY,
                             group_id INTEGER,
                             member_id INTEGER,
                             status TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS group_requests
                            (id INTEGER PRIMARY KEY,
                             requester_id INTEGER,
                             group_id INTEGER,
                             status TEXT)''')
        self.db_connection.commit()

        self.posts_list.bind("<Double-1>", self.show_post_details)

    def show_account(self):
        # Función para mostrar la información de la cuenta del usuario
        messagebox.showinfo("Tu Cuenta", "Aquí va la información de tu cuenta")

    def show_friends(self):
        # Función para mostrar la lista de amigos
        friends_window = tk.Toplevel(self.root)
        friends_window.title("Lista de Amigos")

        friends_listbox = tk.Listbox(friends_window)
        friends_listbox.pack()

        self.cursor.execute("SELECT name FROM friends WHERE status='Amigo'")
        friends = self.cursor.fetchall()
        if friends:
            for friend in friends:
                friends_listbox.insert(tk.END, friend[0])
        else:
            friends_listbox.insert(tk.END, "No tienes amigos")

    def show_groups(self):
        # Función para mostrar la lista de grupos
        groups_window = tk.Toplevel(self.root)
        groups_window.title("Lista de Grupos")

        groups_listbox = tk.Listbox(groups_window)
        groups_listbox.pack()

        self.cursor.execute("SELECT name FROM groups")
        groups = self.cursor.fetchall()
        if groups:
            for group in groups:
                groups_listbox.insert(tk.END, group[0])
        else:
            groups_listbox.insert(tk.END, "No hay grupos disponibles")

    def show_group_requests(self):
        # Función para mostrar las solicitudes de membresía a grupos pendientes
        group_requests_window = tk.Toplevel(self.root)
        group_requests_window.title("Solicitudes de Grupo")

        group_requests_listbox = tk.Listbox(group_requests_window)
        group_requests_listbox.pack()

        self.cursor.execute("SELECT name FROM groups WHERE id IN (SELECT group_id FROM group_requests WHERE requester_id=?)", (current_user_id,))
        group_requests = self.cursor.fetchall()
        if group_requests:
            for request in group_requests:
                group_requests_listbox.insert(tk.END, request[0])
        else:
            group_requests_listbox.insert(tk.END, "No tienes solicitudes de grupo pendientes")

    def show_messages(self):
        # Función para mostrar la lista de mensajes recibidos y enviados
        messages_window = tk.Toplevel(self.root)
        messages_window.title("Mensajes")

        received_messages_label = tk.Label(messages_window, text="Mensajes Recibidos")
        received_messages_label.pack()

        received_messages_listbox = tk.Listbox(messages_window)
        received_messages_listbox.pack()

        self.cursor.execute("SELECT message_text FROM messages WHERE receiver_id=?", (current_user_id,))
        received_messages = self.cursor.fetchall()
        if received_messages:
            for message in received_messages:
                received_messages_listbox.insert(tk.END, message[0])
        else:
            received_messages_listbox.insert(tk.END, "No tienes mensajes recibidos")

        sent_messages_label = tk.Label(messages_window, text="Mensajes Enviados")
        sent_messages_label.pack()

        sent_messages_listbox = tk.Listbox(messages_window)
        sent_messages_listbox.pack()

        self.cursor.execute("SELECT message_text FROM messages WHERE sender_id=?", (current_user_id,))
        sent_messages = self.cursor.fetchall()
        if sent_messages:
            for message in sent_messages:
                sent_messages_listbox.insert(tk.END, message[0])
        else:
            sent_messages_listbox.insert(tk.END, "No tienes mensajes enviados")

    def show_profile(self):
        # Función para mostrar el perfil del usuario y permitir editar la información
        profile_window = tk.Toplevel(self.root)
        profile_window.title("Perfil")

        # Cargar información del perfil desde la base de datos
        self.cursor.execute("SELECT username, profile_picture FROM profile WHERE id=?", (current_user_id,))
        profile_data = self.cursor.fetchone()

        username_label = tk.Label(profile_window, text="Nombre de Usuario:")
        username_label.pack()

        username_entry = tk.Entry(profile_window)
        username_entry.pack()
        username_entry.insert(tk.END, profile_data[0])

        password_label = tk.Label(profile_window, text="Contraseña:")
        password_label.pack()

        password_entry = tk.Entry(profile_window, show="*")
        password_entry.pack()

        confirm_password_label = tk.Label(profile_window, text="Confirmar Contraseña:")
        confirm_password_label.pack()

        confirm_password_entry = tk.Entry(profile_window, show="*")
        confirm_password_entry.pack()

        profile_picture_label = tk.Label(profile_window, text="Foto de Perfil:")
        profile_picture_label.pack()

        profile_picture_path = tk.StringVar()
        profile_picture_path.set(profile_data[1])

        def browse_image():
            filename = filedialog.askopenfilename()
            if filename:
                profile_picture_path.set(filename)

        profile_picture_button = tk.Button(profile_window, text="Seleccionar Imagen", command=browse_image)
        profile_picture_button.pack()

        save_button = tk.Button(profile_window, text="Guardar Cambios", command=lambda: save_profile(profile_window, username_entry.get(), password_entry.get(), confirm_password_entry.get(), profile_picture_path.get()))
        save_button.pack()

    def save_profile(self, window, username, password, confirm_password, profile_picture):
        # Función para guardar los cambios en el perfil del usuario
        if password != confirm_password:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return

        if username:
            self.cursor.execute("UPDATE profile SET username=? WHERE id=?", (username, current_user_id))

        if password:
            self.cursor.execute("UPDATE profile SET password=? WHERE id=?", (password, current_user_id))

        if profile_picture:
            self.cursor.execute("UPDATE profile SET profile_picture=? WHERE id=?", (profile_picture, current_user_id))

        self.db_connection.commit()
        messagebox.showinfo("Perfil", "Cambios guardados correctamente")
        window.destroy()

    def search_friends(self):
        # Función para buscar amigos por nombre
        search_query = self.search_entry.get()
        if search_query:
            search_results_window = tk.Toplevel(self.root)
            search_results_window.title("Resultados de Búsqueda")

            results_listbox = tk.Listbox(search_results_window)
            results_listbox.pack()

            self.cursor.execute("SELECT name FROM friends WHERE name LIKE ?", ('%' + search_query + '%',))
            results = self.cursor.fetchall()
            if results:
                for result in results:
                    results_listbox.insert(tk.END, result[0])
            else:
                results_listbox.insert(tk.END, "No se encontraron resultados")
        else:
            messagebox.showwarning("Búsqueda", "Por favor, ingresa un nombre para buscar")

    def create_post(self):
        # Función para crear una nueva publicación
        post_window = tk.Toplevel(self.root)
        post_window.title("Nueva Publicación")

        def browse_image():
            filename = filedialog.askopenfilename()
            if filename:
                selected_image.config(text=filename)

        def publish_post():
            text = post_text.get("1.0", tk.END).strip()
            image = selected_image.cget("text")
            if text or image:
                self.save_post(text, image)
                self.load_posts()
                post_window.destroy()
            else:
                messagebox.showwarning("Advertencia", "Por favor, ingresa texto o selecciona una imagen.")

        post_text_label = tk.Label(post_window, text="Comentario:")
        post_text_label.pack()

        post_text = tk.Text(post_window, height=4, width=50)
        post_text.pack()

        image_frame = tk.Frame(post_window)
        image_frame.pack()

        browse_button = tk.Button(image_frame, text="Seleccionar imagen", command=browse_image)
        browse_button.grid(row=0, column=0)

        selected_image = tk.Label(image_frame, text="")
        selected_image.grid(row=0, column=1)

        publish_button = tk.Button(post_window, text="Publicar", command=publish_post)
        publish_button.pack()

    def save_post(self, text, image):
        self.cursor.execute("INSERT INTO posts (text, image) VALUES (?, ?)", (text, image))
        self.db_connection.commit()
    def show_post_details(self, event):
        selection = self.posts_list.curselection()
        if selection:
            post_id = int(self.posts_list.get(selection[0]).split(',')[0].split(':')[1].strip())
            post_details_window = tk.Toplevel(self.root)
            post_details_window.title("Detalles de la Publicación")

            text_label = tk.Label(post_details_window, text="Texto:")
            text_label.pack()

            self.cursor.execute("SELECT text FROM posts WHERE id=?", (post_id,))
            post_text = self.cursor.fetchone()[0]
            text_display = tk.Label(post_details_window, text=post_text)
            text_display.pack()

            self.cursor.execute("SELECT image FROM posts WHERE id=?", (post_id,))
            image_path = self.cursor.fetchone()[0]
            if image_path:
                image_display = tk.Label(post_details_window, text="Imagen adjunta: " + os.path.basename(image_path))
                image_display.pack()

            like_button = tk.Button(post_details_window, text="Me gusta", command=lambda: self.react_to_post(post_id, like=True))
            like_button.pack()

            dislike_button = tk.Button(post_details_window, text="No me gusta", command=lambda: self.react_to_post(post_id, like=False))
            dislike_button.pack()

            self.load_comments(post_details_window, post_id)

            delete_post_button = tk.Button(post_details_window, text="Eliminar Publicación", command=lambda: self.delete_post(post_id))
            delete_post_button.pack()

    def react_to_post(self, post_id, like=True):
        if like:
            self.cursor.execute("UPDATE posts SET likes = likes + 1 WHERE id=?", (post_id,))
        else:
            self.cursor.execute("UPDATE posts SET dislikes = dislikes + 1 WHERE id=?", (post_id,))
        self.db_connection.commit()
        self.load_posts()

    def delete_post(self, post_id):
        confirmation = messagebox.askyesno("Eliminar Publicación", "¿Estás seguro de que quieres eliminar esta publicación?")
        if confirmation:
            self.cursor.execute("DELETE FROM posts WHERE id=?", (post_id,))
            self.cursor.execute("DELETE FROM comments WHERE post_id=?", (post_id,))
            self.db_connection.commit()
            self.load_posts()

    def load_comments(self, window, post_id):
        comments_frame = tk.Frame(window)
        comments_frame.pack()

        comment_label = tk.Label(comments_frame, text="Comentarios:")
        comment_label.pack()

        self.cursor.execute("SELECT comment_text FROM comments WHERE post_id=?", (post_id,))
        comments = self.cursor.fetchall()
        if comments:
            for comment in comments:
                comment_label = tk.Label(comments_frame, text=comment[0])
                comment_label.pack()
        else:
            no_comments_label = tk.Label(comments_frame, text="No hay comentarios")
            no_comments_label.pack()

root = tk.Tk()
app = PipoBookApp(root)
root.mainloop()
