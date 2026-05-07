import tkinter as tk
from tkinter import messagebox, scrolledtext
import json
import os
import urllib.request
import urllib.error

FAVORITES_FILE = "favorites.json"


class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("600x500")

        tk.Label(root, text="Введите имя пользователя GitHub:", font=("Arial", 10, "bold")).pack(pady=5)
        self.input_entry = tk.Entry(root, width=40)
        self.input_entry.pack(pady=5)

        self.search_btn = tk.Button(root, text="Найти", command=self.search_user)
        self.search_btn.pack(pady=5)

        self.result_list = scrolledtext.ScrolledText(root, height=10)
        self.result_list.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        self.add_btn = tk.Button(root, text="Добавить выбранного в избранное", command=self.add_to_favorites)
        self.add_btn.pack(pady=5)

        self.show_fav_btn = tk.Button(root, text="Показать избранное", command=self.show_favorites)
        self.show_fav_btn.pack(pady=5)

        self.load_favorites()

    def search_user(self):
        username = self.input_entry.get().strip()
        if not username:
            messagebox.showwarning("Ошибка", "Поле поиска не может быть пустым!")
            return

        url = f"https://api.github.com/users/{username}"

        try:
            # Использование встроенного urllib вместо requests
            with urllib.request.urlopen(url) as response:
                data = response.read()
                user_data = json.loads(data)

                output = (
                    f"Имя: {user_data.get('name', 'Не указано')}\n"
                    f"Логин: {user_data.get('login')}\n"
                    f"Репозитории: {user_data.get('public_repos')}\n"
                    f"Подписчики: {user_data.get('followers')}\n"
                    f"URL: {user_data.get('html_url')}\n"
                    f"-----------------------"
                )
                self.result_list.delete(1.0, tk.END)
                self.result_list.insert(tk.END, output)

        except urllib.error.HTTPError as e:
            if e.code == 404:
                messagebox.showerror("Ошибка", f"Пользователь '{username}' не найден.")
            else:
                messagebox.showerror("Ошибка", f"Ошибка API GitHub: {e.code}")
        except Exception as e:
            messagebox.showerror("Ошибка соединения", f"Проверьте интернет соединение: {str(e)}")

    def add_to_favorites(self):
        text_content = self.result_list.get(1.0, tk.END).strip()
        if not text_content:
            messagebox.showinfo("Инфо", "Сначала найдите пользователя.")
            return

        lines = text_content.split('\n')
        login = None
        for line in lines:
            if line.startswith("Логин:"):
                login = line.replace("Логин:", "").strip()
                break

        if login:
            if login not in self.favorites:
                self.favorites.append(login)
                self.save_favorites()
                messagebox.showinfo("Успех", f"Пользователь '{login}' добавлен в избранное!")
            else:
                messagebox.showinfo("Инфо", f"Пользователь '{login}' уже в избранном.")
        else:
            messagebox.showerror("Ошибка", "Не удалось извлечь логин пользователя.")

    def load_favorites(self):
        if os.path.exists(FAVORITES_FILE):
            try:
                with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
                    self.favorites = json.load(f)
            except:
                self.favorites = []
        else:
            self.favorites = []

    def save_favorites(self):
        with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.favorites, f, ensure_ascii=False, indent=4)

    def show_favorites(self):
        if not self.favorites:
            messagebox.showinfo("Избранное", "Список избранных пользователей пуст.")
            return

        msg = "Ваши избранные пользователи:\n" + "\n".join(self.favorites)
        messagebox.showinfo("Избранное", msg)


if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()