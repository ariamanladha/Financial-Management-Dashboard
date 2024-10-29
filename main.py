import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb

from expense import ExpenseTab
from Income import IncomeTab
from savings import SavingsTab
from investments import InvestmentTab
from goals import GoalsTab

class FinanceDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Finance Management Dashboard")
        self.root.geometry('1000x700')

        # Initialize the ttkbootstrap style
        style = tb.Style("lumen")

        # Create the notebook
        self.notebook = ttk.Notebook(self.root, style='primary.TNotebook')

        # Create tabs
        self.investmentsTabFrame = ttk.Frame(self.notebook)
        self.incomeTabFrame = ttk.Frame(self.notebook)
        self.expensesTabFrame = ttk.Frame(self.notebook)
        self.savingsTabFrame = ttk.Frame(self.notebook)
        self.goalsTabFrame = ttk.Frame(self.notebook)

        # Add tabs to the notebook
        self.notebook.add(self.investmentsTabFrame, text="Investments")
        self.notebook.add(self.incomeTabFrame, text="Income")
        self.notebook.add(self.expensesTabFrame, text="Expenses")
        self.notebook.add(self.savingsTabFrame, text="Savings")
        self.notebook.add(self.goalsTabFrame, text="Goals & Recommendations")

        # Pack the notebook
        self.notebook.pack(expand=True, fill="both")

        # Setup tab contents
        self.setupInvestmentsTab()
        self.setupIncomeTab()
        self.setupExpensesTab()
        self.setupSavingsTab()
        self.setupGoalsTab()

    def setupInvestmentsTab(self):
        self.investmentsTab = InvestmentTab(self.investmentsTabFrame)

    def setupIncomeTab(self):
        self.incomeTab = IncomeTab(self.incomeTabFrame)

    def setupExpensesTab(self):
        self.expensesTab = ExpenseTab(self.expensesTabFrame)

    def setupSavingsTab(self):
        self.savingsTab = SavingsTab(self.savingsTabFrame)

    def setupGoalsTab(self):
        self.goalsTab = GoalsTab(self.goalsTabFrame)

if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceDashboard(root)
    root.mainloop()
