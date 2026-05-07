import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
from datetime import datetime

class CurrencyConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("600x400")

        # Список валют (можно расширить)
        self.currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY', 'RUB', 'INR']

        # Выбор валюты "из"
        ttk.Label(root, text="Из:").grid(row=0, column=0, padx=10, pady=10)
        self.from_currency = ttk.Combobox(root, values=self.currencies)
        self.from_currency.grid(row=0, column=1, padx=10, pady=10)

        # Выбор валюты "в"
        ttk.Label(root, text="В:").grid(row=1, column=0, padx=10, pady=10)
        self.to_currency = ttk.Combobox(root, values=self.currencies)
        self.to_currency.grid(row=1, column=1, padx=10, pady=10)

        # Поле ввода суммы
        ttk.Label(root, text="Сумма:").grid(row=2, column=0, padx=10, pady=10)
        self.amount_entry = ttk.Entry(root)
        self.amount_entry.grid(row=2, column=1, padx=10, pady=10)

        # Кнопка конвертации
        self.convert_button = ttk.Button(root, text="Конвертировать", command=self.convert)
        self.convert_button.grid(row=3, column=0, columnspan=2, pady=20)

        # Таблица истории
        self.history_tree = ttk.Treeview(root, columns=("From", "To", "Amount", "Result"), show="headings")
        self.history_tree.heading("From", text="Из")
        self.history_tree.heading("To", text="В")
        self.history_tree.heading("Amount", text="Сумма")
        self.history_tree.heading("Result", text="Результат")
        self.history_tree.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Настройка растягивания таблицы
        root.grid_rowconfigure(4, weight=1)
        root.grid_columnconfigure(1, weight=1)

        # Загрузка истории при запуске
        self.update_history_table()

    def get_exchange_rate(self, from_currency, to_currency):
        api_key = "YOUR_API_KEY"  # Замените на ваш API‑ключ
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        try:
            response = requests.get(url)
            data = response.json()
            if to_currency in data["rates"]:
                return data["rates"][to_currency]
            else:
                messagebox.showerror("Ошибка", "Валюта не найдена")
                return None
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка подключения: {e}")
            return None

    def load_history(self):
        try:
            with open("history.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_history(self, history):
        with open("history.json", "w") as f:
            json.dump(history, f, indent=4)

    def add_to_history(self, from_curr, to_curr, amount, result):
        history = self.load_history()
        history.append({
            "from": from_curr,
            "to": to_curr,
            "amount": amount,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        self.save_history(history)
        self.update_history_table()

    def update_history_table(self):
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        history = self.load_history()
        for record in history:
            self.history_tree.insert("", "end", values=(
                record["from"],
                record["to"],
                record["amount"],
                f"{record['result']:.2f}"
            ))

    def convert(self):
        from_curr = self.from_currency.get()
        to_curr = self.to_currency.get()
        amount_str = self.amount_entry.get()

        # Проверка валюты
        if not from_curr or not to_curr:
            messagebox.showerror("Ошибка", "Выберите валюты")
            return

        # Проверка суммы
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Введите положительное число")
            return

        # Получение курса и расчёт
        rate = self.get_exchange_rate(from_curr, to_curr)
        if rate:
            result = amount * rate
            messagebox.showinfo("Результат", f"{amount} {from_curr} = {result:.2f} {to_curr}")
            self.add_to_history(from_curr, to_curr, amount, result)


def main():
    root = tk.Tk()
    app = CurrencyConverterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()