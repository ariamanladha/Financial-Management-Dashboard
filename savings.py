import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime as dt
import matplotlib.dates as mdates

class SavingsTab:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(self.parent, style='TFrame')
        self.frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Configure column and row weights for responsiveness
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        self.frame.rowconfigure(2, weight=1)
        self.frame.rowconfigure(3, weight=3)

        self.totalSavings = self.calculateSavings()
        self.totalIncome = self.getTotalIncome()
        self.createBigSavingsLabel()
        self.createSavingsPercentageLabel()
        self.createInterestCalculator()
        self.createSavingsHistoryChart()

    def createBigSavingsLabel(self):
        self.bigSavingsLabel = ttk.Label(self.frame, text=f"Total Savings: ${self.totalSavings:.2f}", style="success.TLabel", font=('Arial', 15))
        self.bigSavingsLabel.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

    def createSavingsPercentageLabel(self):
        savingsPercentage = (self.totalSavings / self.totalIncome) * 100 if self.totalIncome != 0 else 0
        self.savingsPercentageLabel = ttk.Label(self.frame, text=f"Savings as Percentage of Income: {savingsPercentage:.2f}%", style="success.TLabel", font=('Arial', 15))
        self.savingsPercentageLabel.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

    def createInterestCalculator(self):
        calculatorFrame = ttk.LabelFrame(self.frame, text="Interest Calculator", style="primary.TLabelframe")
        calculatorFrame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        ttk.Label(calculatorFrame, text="Principal Amount:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.principalEntry = ttk.Entry(calculatorFrame)
        self.principalEntry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(calculatorFrame, text="Annual Interest Rate (%):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.rateEntry = ttk.Entry(calculatorFrame)
        self.rateEntry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(calculatorFrame, text="Time (years):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.timeEntry = ttk.Entry(calculatorFrame)
        self.timeEntry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(calculatorFrame, text="Compounding Periods per Year:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.compoundingEntry = ttk.Entry(calculatorFrame)
        self.compoundingEntry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        self.calculateButton = ttk.Button(calculatorFrame, text="Calculate", command=self.calculateInterest)
        self.calculateButton.grid(row=4, column=0, columnspan=2, padx=5, pady=10)

        self.resultLabel = ttk.Label(calculatorFrame, text="", style="primary.TLabel")
        self.resultLabel.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

    def calculateInterest(self):
        try:
            principal = float(self.principalEntry.get())
            rate = float(self.rateEntry.get()) / 100
            time = float(self.timeEntry.get())
            compoundingPeriods = int(self.compoundingEntry.get())

            # Compound Interest Formula
            futureValue = principal * (1 + rate / compoundingPeriods) ** (compoundingPeriods * time)
            self.resultLabel.config(text=f"Future Value: ${futureValue:.2f}")
        except ValueError:
            self.resultLabel.config(text="Invalid input. Please enter numeric values.")

    def createSavingsHistoryChart(self):
        chartFrame = ttk.LabelFrame(self.frame, text="Savings History Chart", style="primary.TLabelframe")
        chartFrame.grid(row=2, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")

        fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(fig, master=chartFrame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.updateSavingsHistoryChart()

    def updateSavingsHistoryChart(self):
        self.ax.clear()
        savingsHistory = self.getSavingsHistory()
        if savingsHistory:
            dates, amounts = zip(*savingsHistory)
            self.ax.plot(dates, amounts, marker='o', linestyle='-', color='b')
            self.ax.set_title('Historical Savings by Month')
            self.ax.set_ylabel('Amount')
            self.ax.set_xlabel('Date')
            self.ax.grid(True)
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%y'))
            plt.setp(self.ax.get_xticklabels(), rotation=45, ha="right", fontsize=10)
        self.canvas.draw()

    def calculateSavings(self):
        totalIncome = self.getTotalIncome()
        totalExpense = self.getTotalExpense()
        return totalIncome - totalExpense

    def getSavingsHistory(self):
        conn = sqlite3.connect('finance.db')
        c = conn.cursor()
        c.execute('''
            SELECT strftime('%Y-%m', date) as month, 
                   SUM(CASE WHEN type='income' THEN amount ELSE -amount END) as savings
            FROM (
                SELECT date, amount, 'income' as type FROM income
                UNION ALL
                SELECT date, amount, 'expense' as type FROM expenses
            )
            GROUP BY month
            ORDER BY month DESC
            LIMIT 12
        ''')
        savings = c.fetchall()
        conn.close()
        savings.reverse()  # Reverse to show in ascending order by date
        return [(dt.datetime.strptime(month, '%Y-%m'), amount) for month, amount in savings]

    def getTotalIncome(self):
        conn = sqlite3.connect('finance.db')
        c = conn.cursor()
        c.execute('SELECT SUM(amount) FROM income')
        totalIncome = c.fetchone()[0] or 0
        conn.close()
        return totalIncome

    def getTotalExpense(self):
        conn = sqlite3.connect('finance.db')
        c = conn.cursor()
        c.execute('SELECT SUM(amount) FROM expenses')
        totalExpense = c.fetchone()[0] or 0
        conn.close()
        return totalExpense
