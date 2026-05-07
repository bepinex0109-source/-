import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

DATA_FILE = "expenses.json"

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("800x600")

        # Данные
        self.expenses = []
        self.load_data()

        # --- Верхняя часть: Форма добавления ---
        input_frame = ttk.LabelFrame(root, text="Добавить расход", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Сумма
        ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0, padx=5)
        self.amount_entry = ttk.Entry(input_frame, width=15)
        self.amount_entry.grid(row=0, column=1, padx=5)

        # Категория
        ttk.Label(input_frame, text="Категория:").grid(row=0, column=2, padx=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var, values=["Еда", "Транспорт", "Развлечения", "Одежда", "Здоровье", "Прочее"])
        self.category_combo.grid(row=0, column=3, padx=5)
        self.category_combo.current(0)

        # Дата
        ttk.Label(input_frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=4, padx=5)
        self.date_entry = ttk.Entry(input_frame, width=12)
        self.date_entry.grid(row=0, column=5, padx=5)
        # Подсказка
        self.date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))

        # Кнопка добавления
        self.add_btn = ttk.Button(input_frame, text="Добавить расход", command=self.add_expense)
        self.add_btn.grid(row=0, column=6, padx=10, pady=5)

        # --- Средняя часть: Таблица ---
        tree_frame = ttk.LabelFrame(root, text="Все расходы", padding=5)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("ID", "Сумма", "Категория", "Дата")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        self.tree.heading("ID", text="#")
        self.tree.heading("Сумма", text="Сумма")
        self.tree.heading("Категория", text="Категория")
        self.tree.heading("Дата", text="Дата")
        
        self.tree.column("ID", width=40, anchor="center")
        self.tree.column("Сумма", width=80, anchor="center")
        self.tree.column("Категория", width=120, anchor="center")
        self.tree.column("Дата", width=100, anchor="center")
        
        self.tree.pack(fill="both", expand=True)

        # --- Нижняя часть: Фильтры и итоги ---
        filter_frame = ttk.LabelFrame(root, text="Фильтрация и подсчет", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Фильтр категории
        ttk.Label(filter_frame, text="Категория:").pack(side="left", padx=5)
        self.filter_category_var = tk.StringVar(value="Все")
        self.filter_category_combo = ttk.Combobox(filter_frame, textvariable=self.filter_category_var, values=["Все", "Еда", "Транспорт", "Развлечения", "Одежда", "Здоровье", "Прочее"], width=10)
        self.filter_category_combo.pack(side="left", padx=5)

        # Фильтр даты (от и до)
        ttk.Label(filter_frame, text="Дата от:").pack(side="left", padx=5)
        self.date_from_entry = ttk.Entry(filter_frame, width=12)
        self.date_from_entry.pack(side="left", padx=5)
        
        ttk.Label(filter_frame, text="Дата до:").pack(side="left", padx=5)
        self.date_to_entry = ttk.Entry(filter_frame, width=12)
        self.date_to_entry.pack(side="left", padx=5)

        # Кнопка применить фильтр
        self.apply_filter_btn = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        self.apply_filter_btn.pack(side="left", padx=10)

        # Кнопка сбросить фильтр
        self.reset_filter_btn = ttk.Button(filter_frame, text="Сброс", command=self.reset_filter)
        self.reset_filter_btn.pack(side="left", padx=5)

        # Метка суммы
        self.total_label = ttk.Label(filter_frame, text="Итого: 0.00 ₽", font=("Arial", 12, "bold"), foreground="green")
        self.total_label.pack(side="right", padx=20)

        # Кнопка удалить запись
        self.delete_btn = ttk.Button(filter_frame, text="Удалить выбранное", command=self.delete_expense)
        self.delete_btn.pack(side="right", padx=5)

        # Инициализация таблицы
        self.refresh_table()

    def load_data(self):
        """Загружает данные из JSON"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    self.expenses = json.load(f)
            except:
                self.expenses = []
        else:
            self.expenses = []

    def save_data(self):
        """Сохраняет данные в JSON"""
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.expenses, f, ensure_ascii=False, indent=4)

    def validate_date(self, date_str):
        """Проверка формата даты ДД.ММ.ГГГГ"""
        try:
            datetime.strptime(date_str, "%d.%m.%Y")
            return True
        except ValueError:
            return False

    def add_expense(self):
        """Добавляет новый расход (пункт 2)"""
        amount_str = self.amount_entry.get().strip()
        category = self.category_var.get()
        date_str = self.date_entry.get().strip()

        # Проверка корректности ввода (пункт 6)
        if not amount_str:
            messagebox.showerror("Ошибка", "Поле 'Сумма' не может быть пустым")
            return
        
        if not category:
            messagebox.showerror("Ошибка", "Выберите категорию")
            return

        # Проверка на число
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат суммы")
            return

        # Проверка даты
        if not self.validate_date(date_str):
            messagebox.showerror("Ошибка", "Некорректный формат даты. Используйте ДД.ММ.ГГГГ")
            return

        # Создание записи
        expense = {
            "id": len(self.expenses) + 1,
            "amount": amount,
            "category": category,
            "date": date_str
        }
        
        self.expenses.append(expense)
        self.save_data()
        self.refresh_table()
        
        self.amount_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
        
        messagebox.showinfo("Успех", "Расход добавлен!")

    def refresh_table(self, filtered_data=None):
        """Обновляет таблицу"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        data_to_show = filtered_data if filtered_data is not None else self.expenses
        
        for expense in data_to_show:
            self.tree.insert("", tk.END, values=(
                expense["id"],
                f"{expense['amount']:.2f}",
                expense["category"],
                expense["date"]
            ))

        # Подсчет суммы (пункт 3)
        if data_to_show:
            total = sum(item["amount"] for item in data_to_show)
            self.total_label.config(text=f"Итого: {total:.2f} ₽")
        else:
            self.total_label.config(text="Итого: 0.00 ₽")

    def apply_filter(self):
        """Фильтрация по категории и дате (пункт 4)"""
        filter_category = self.filter_category_var.get()
        date_from_str = self.date_from_entry.get().strip()
        date_to_str = self.date_to_entry.get().strip()

        filtered = []
        
        # Функция для преобразования строки даты в объект для сравнения
        def str_to_date(s):
            try:
                return datetime.strptime(s, "%d.%m.%Y").date()
            except:
                return None

        date_from = str_to_date(date_from_str) if date_from_str else None
        date_to = str_to_date(date_to_str) if date_to_str else None

        for expense in self.expenses:
            # Фильтр категории
            if filter_category != "Все" and expense["category"] != filter_category:
                continue
            
            exp_date = str_to_date(expense["date"])
            if exp_date is None:
                continue

            # Фильтр даты от
            if date_from and exp_date < date_from:
                continue

            # Фильтр даты до
            if date_to and exp_date > date_to:
                continue

            filtered.append(expense)

        self.refresh_table(filtered)

    def reset_filter(self):
        """Сбрасывает фильтры"""
        self.filter_category_var.set("Все")
        self.date_from_entry.delete(0, tk.END)
        self.date_to_entry.delete(0, tk.END)
        self.refresh_table()

    def delete_expense(self):
        """Удаляет выбранную запись"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Внимание", "Выберите запись для удаления")
            return

        item_values = self.tree.item(selected_item)["values"]
        expense_id = int(item_values[0])

        # Удаляем из списка
        self.expenses = [e for e in self.expenses if e["id"] != expense_id]
        
        # Пересоздаем ID для порядка
        for idx, expense in enumerate(self.expenses):
            expense["id"] = idx + 1

        self.save_data()
        self.apply_filter()  # Обновить с текущими фильтрами

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
