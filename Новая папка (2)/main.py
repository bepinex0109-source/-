import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
from datetime import datetime

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("800x600")

        # Поле ввода для поиска
        ttk.Label(root, text="Имя пользователя GitHub:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.search_entry = ttk.Entry(root, width=40)
        self.search_entry.grid(row=0, column=1, padx=10, pady=10)

        # Кнопка поиска
        self.search_button = ttk.Button(root, text="Найти", command=self.search_user)
        self.search_button.grid(row=0, column=2, padx=10, pady=10)

        # Список результатов поиска
        ttk.Label(root, text="Результаты поиска:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.results_tree = ttk.Treeview(root, columns=("Username", "Name", "Public Repos", "Followers"), show="headings", height=15)
        self.results_tree.heading("Username", text="Username")
        self.results_tree.heading("Name", text="Name")
        self.results_tree.heading("Public Repos", text="Public Repos")
        self.results_tree.heading("Followers", text="Followers")
        self.results_tree.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # Прокрутка для списка
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.results_tree.yview)
        scrollbar.grid(row=2, column=3, sticky="ns")
        self.results_tree.configure(yscrollcommand=scrollbar.set)

        # Кнопка добавления в избранное
        self.add_favorite_button = ttk.Button(root, text="Добавить в избранное", command=self.add_to_favorites)
        self.add_favorite_button.grid(row=3, column=0, padx=10, pady=10)

        # Список избранных пользователей
        ttk.Label(root, text="Избранные пользователи:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.favorites_tree = ttk.Treeview(root, columns=("Username", "Name", "Added Date"), show="headings", height=8)
        self.favorites_tree.heading("Username", text="Username")
        self.favorites_tree.heading("Name", text="Name")
        self.favorites_tree.heading("Added Date", text="Added Date")
        self.favorites_tree.grid(row=5, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # Настройка растягивания элементов
        root.grid_rowconfigure(2, weight=1)
        root.grid_rowconfigure(5, weight=1)
        root.grid_columnconfigure(1, weight=1)

        # Загрузка избранных пользователей при запуске
        self.load_favorites()
        self.update_favorites_table()

    def search_user(self):
        username = self.search_entry.get().strip()

        # Проверка на пустой ввод
        if not username:
            messagebox.showerror("Ошибка", "Поле поиска не должно быть пустым")
            return

        try:
            # Запрос к GitHub API
            url = f"https://api.github.com/users/{username}"
            response = requests.get(url)

            if response.status_code == 200:
                user_data = response.json()
                self.display_search_result(user_data)
            elif response.status_code == 404:
                messagebox.showerror("Ошибка", f"Пользователь '{username}' не найден")
            else:
                messagebox.showerror("Ошибка", f"Ошибка GitHub API: {response.status_code}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка подключения: {e}")

    def display_search_result(self, user_data):
        # Очистка предыдущих результатов
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        # Добавление нового результата
        self.results_tree.insert("", "end", values=(
            user_data.get("login", "N/A"),
            user_data.get("name", "N/A"),
            user_data.get("public_repos", 0),
            user_data.get("followers", 0)
        ))

    def add_to_favorites(self):
        # Получение выбранного пользователя из результатов поиска
        selected = self.results_tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите пользователя из результатов поиска")
            return

        values = self.results_tree.item(selected[0])["values"]
        username, name = values[0], values[1]

        # Загрузка текущих избранных
        favorites = self.load_favorites()

        # Проверка, не добавлен ли уже пользователь
        if any(fav["username"] == username for fav in favorites):
            messagebox.showinfo("Информация", f"Пользователь '{username}' уже в избранном")
            return

        # Добавление в избранное
        favorites.append({
            "username": username,
            "name": name,
            "added_date": datetime.now().isoformat()
        })
        self.save_favorites(favorites)
        self.update_favorites_table()
        messagebox.showinfo("Успех", f"Пользователь '{username}' добавлен в избранное")

    def load_favorites(self):
        try:
            with open("favorites.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_favorites(self, favorites):
        with open("favorites.json", "w") as f:
            json.dump(favorites, f, indent=4)

    def update_favorites_table(self):
        # Очистка таблицы
        for item in self.favorites_tree.get_children():
            self.favorites_tree.delete(item)

        # Обновление таблицы
        favorites = self.load_favorites()
        for fav in favorites:
            self.favorites_tree.insert("", "end", values=(
                fav["username"],
                fav["name"],
                datetime.fromisoformat(fav["added_date"]).strftime("%Y-%m-%d %H:%M")
            ))

def main():
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()

if __name__ == "__main__":
    main()
