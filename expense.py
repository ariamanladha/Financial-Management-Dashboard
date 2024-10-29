import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime as dt

class ExpenseTab:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(self.parent, style='TFrame')
        self.frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=3)
        self.frame.rowconfigure(0, weight=1)

        self.leftFrame = ttk.LabelFrame(self.frame, text="Add Expense", style="primary.TLabelframe")
        self.leftFrame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.amountLabel = ttk.Label(self.leftFrame, text="Amount:")
        self.amountLabel.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.amountEntry = ttk.Entry(self.leftFrame)
        self.amountEntry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.categoryLabel = ttk.Label(self.leftFrame, text="Category:")
        self.categoryLabel.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.categoryVar = tk.StringVar()
        self.categoryCombobox = ttk.Combobox(self.leftFrame, textvariable=self.categoryVar)
        self.categoryCombobox['values'] = ('Food', 'Transport', 'Entertainment', 'Other')
        self.categoryCombobox.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.addButton = ttk.Button(self.leftFrame, text="Add Expense", command=self.addExpense)
        self.addButton.grid(row=2, column=0, columnspan=2, padx=5, pady=10)

        self.rightFrame = ttk.Frame(self.frame, style="TFrame")
        self.rightFrame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.rightFrame.rowconfigure(0, weight=3)
        self.rightFrame.rowconfigure(1, weight=1)

        self.expenseData = self.getExpenseData()
        self.createBarChart()
        self.totalExpenseLabel = ttk.Label(self.rightFrame, text=f"Total Expense: ${self.getTotalExpense():.2f}", style="danger.TLabel", font=('Arial', 20))
        self.totalExpenseLabel.grid(row=1, column=0, padx=5, pady=5, sticky="w")

    def addExpense(self):
        try:
            amount = float(self.amountEntry.get())
            category = self.categoryVar.get()
            if category:
                self.saveExpenseToDb(amount, category)
                self.expenseData = self.getExpenseData()
                self.updateBarChart()
                self.updateTotalExpense()
        except ValueError:
            pass

    def createBarChart(self):
        fig, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(fig, master=self.rightFrame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        self.updateBarChart()

    def updateBarChart(self):
        self.ax.clear()
        categories = list(self.expenseData.keys())
        amounts = list(self.expenseData.values())
        self.ax.bar(categories, amounts, color='red')
        self.ax.set_title('Expenses by Category', fontsize=8)
        self.ax.set_ylabel('Amount', fontsize=7)
        self.ax.set_xlabel('Category', fontsize=7)
        self.ax.tick_params(axis='both', which='major', labelsize=7)
        self.canvas.draw()

    def updateTotalExpense(self):
        totalExpense = self.getTotalExpense()
        self.totalExpenseLabel.config(text=f"Total Expense: ${totalExpense:.2f}")

    def saveExpenseToDb(self, amount, category):
        conn = sqlite3.connect('finance.db')
        c = conn.cursor()
        c.execute('INSERT INTO expenses (date, amount, category) VALUES (?, ?, ?)', (dt.datetime.now().strftime('%Y-%m-%d'), amount, category))
        conn.commit()
        conn.close()

    def getExpenseData(self):
        conn = sqlite3.connect('finance.db')
        c = conn.cursor()
        c.execute('SELECT category, SUM(amount) FROM expenses GROUP BY category')
        data = c.fetchall()
        conn.close()
        return {row[0]: row[1] for row in data}

    def getTotalExpense(self):
        conn = sqlite3.connect('finance.db')
        c = conn.cursor()
        c.execute('SELECT SUM(amount) FROM expenses')
        totalExpense = c.fetchone()[0] or 0
        conn.close()
        return totalExpense

    def getTotalExpenseByCategory(self, category):
        conn = sqlite3.connect('finance.db')
        c = conn.cursor()
        c.execute('SELECT SUM(amount) FROM expenses WHERE category = ?', (category,))
        totalExpense = c.fetchone()[0] or 0
        conn.close()
        return totalExpense
