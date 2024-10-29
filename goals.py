import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, scrolledtext
import sqlite3
import datetime as dt

class GoalsTab:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(self.parent, style='TFrame')
        self.frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        self.frame.rowconfigure(2, weight=3)

        self.create_goal_entry()
        self.update_goals_view()

    def create_goal_entry(self):
        entry_frame = ttk.LabelFrame(self.frame, text="Set a Goal", style="primary.TLabelframe")
        entry_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.goal_type_label = ttk.Label(entry_frame, text="Goal Type:")
        self.goal_type_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.goal_type_var = tk.StringVar()
        self.goal_type_combobox = ttk.Combobox(entry_frame, textvariable=self.goal_type_var)
        self.goal_type_combobox['values'] = ('Income', 'Expenses', 'Savings', 'Investments')
        self.goal_type_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.goal_category_label = ttk.Label(entry_frame, text="Goal Category:")
        self.goal_category_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.goal_category_var = tk.StringVar()
        self.goal_category_combobox = ttk.Combobox(entry_frame, textvariable=self.goal_category_var)
        self.goal_category_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.goal_amount_label = ttk.Label(entry_frame, text="Goal Amount:")
        self.goal_amount_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.goal_amount_entry = ttk.Entry(entry_frame)
        self.goal_amount_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        self.set_goal_button = ttk.Button(entry_frame, text="Set Goal", command=self.set_goal)
        self.set_goal_button.grid(row=3, column=0, columnspan=2, padx=5, pady=10)

        self.goal_type_combobox.bind("<<ComboboxSelected>>", self.update_goal_categories)

    def update_goal_categories(self, event):
        goal_type = self.goal_type_var.get()
        if goal_type == 'Income':
            self.goal_category_combobox['values'] = ('Salary', 'Business', 'Investment', 'Dividends', 'Other')
        elif goal_type == 'Expenses':
            self.goal_category_combobox['values'] = ('Food', 'Transport', 'Entertainment', 'Other')
        elif goal_type == 'Savings':
            self.goal_category_combobox['values'] = ('Total Savings',)
        elif goal_type == 'Investments':
            self.goal_category_combobox['values'] = ('Total Investments',)

    def set_goal(self):
        goal_type = self.goal_type_var.get()
        goal_category = self.goal_category_var.get()
        goal_amount = float(self.goal_amount_entry.get())
        self.save_goal_to_db(goal_type, goal_category, goal_amount)
        self.update_goals_view()

    def save_goal_to_db(self, goal_type, goal_category, goal_amount):
        conn = sqlite3.connect('finance.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO financial_goals (goal_type, goal_category, goal_amount, progress)
            VALUES (?, ?, ?, 0)
            ON CONFLICT(goal_type, goal_category) DO UPDATE SET goal_amount=excluded.goal_amount
        ''', (goal_type, goal_category, goal_amount))
        conn.commit()
        conn.close()

    def update_goals_view(self):
        goals_frame = ttk.LabelFrame(self.frame, text="Goals Progress", style="primary.TLabelframe")
        goals_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        goals = self.get_goals_data()
        for widget in goals_frame.winfo_children():
            widget.destroy()

        for goal in goals:
            goal_type, goal_category, goal_amount, progress = goal
            progress = self.calculate_progress(goal_type, goal_category, goal_amount)
            progress_bar = ttk.Progressbar(goals_frame, maximum=goal_amount, value=progress)
            progress_bar.pack(fill=tk.X, padx=5, pady=5)
            progress_label = ttk.Label(goals_frame, text=f"{goal_type} - {goal_category}: ${progress:.2f} / ${goal_amount:.2f}")
            progress_label.pack(fill=tk.X, padx=5, pady=5)
            recommendations = self.get_recommendations(goal_type, progress, goal_amount)
            recommendations_label = ttk.Label(goals_frame, text=f"Recommendations: {recommendations}")
            recommendations_label.pack(fill=tk.X, padx=5, pady=5)

    def calculate_progress(self, goal_type, goal_category, goal_amount):
        conn = sqlite3.connect('finance.db')
        c = conn.cursor()
        if goal_type == 'Income':
            c.execute('SELECT SUM(amount) FROM income WHERE category = ?', (goal_category,))
        elif goal_type == 'Expenses':
            c.execute('SELECT SUM(amount) FROM expenses WHERE category = ?', (goal_category,))
        elif goal_type == 'Savings':
            total_income = self.get_total_income(c)
            total_expense = self.get_total_expense(c)
            progress = total_income - total_expense
            return progress
        elif goal_type == 'Investments':
            total_investment, total_profit_loss = self.get_total_investments()
            progress = total_investment + total_profit_loss
            return progress
        progress = c.fetchone()[0] or 0
        conn.close()
        return progress

    def get_total_income(self, cursor):
        cursor.execute('SELECT SUM(amount) FROM income')
        return cursor.fetchone()[0] or 0

    def get_total_expense(self, cursor):
        cursor.execute('SELECT SUM(amount) FROM expenses')
        return cursor.fetchone()[0] or 0

    def get_total_investments(self):
        conn = sqlite3.connect('finance.db')
        c = conn.cursor()
        c.execute('SELECT SUM(shares * purchase_price) FROM investments')
        total_investment = c.fetchone()[0] or 0
        c.execute('SELECT SUM(profit_loss) FROM sales')
        total_profit_loss = c.fetchone()[0] or 0
        conn.close()
        return total_investment, total_profit_loss

    def get_recommendations(self, goal_type, progress, goal_amount):
        if goal_type == 'Income':
            if progress < goal_amount * 0.5:
                return (
                    "You are far from your goal. Consider the following strategies:\n"
                    "- Look for additional sources of income, such as freelancing, part-time jobs, or passive income streams.\n"
                    "- Seek a raise or promotion at your current job by demonstrating your value and accomplishments.\n"
                    "- Enhance your skills through courses and certifications to qualify for higher-paying positions."
                )
            elif progress < goal_amount:
                return (
                    "You are on track. Keep up the good work and explore these opportunities:\n"
                    "- Continue to look for side gigs or freelance work to supplement your income.\n"
                    "- Network with professionals in your field to discover new job opportunities and career growth.\n"
                    "- Invest in your personal development to stay competitive in the job market."
                )
            else:
                return (
                    "Congratulations! You've met your income goal. Here are some next steps:\n"
                    "- Consider setting a new, higher income goal to continue your financial growth.\n"
                    "- Diversify your income sources to reduce risk and increase stability.\n"
                    "- Invest extra income into savings, retirement accounts, or other investments."
                )
        elif goal_type == 'Expenses':
            if progress > goal_amount * 1.5:
                return (
                    "You have exceeded your expense goal by a significant amount. Here are some tips to re-evaluate your spending:\n"
                    "- Create a detailed budget to track your income and expenses more accurately.\n"
                    "- Identify and eliminate unnecessary expenses, such as subscriptions you no longer use.\n"
                    "- Consider cheaper alternatives for essential expenses, like cooking at home instead of dining out."
                )
            elif progress > goal_amount:
                return (
                    "You have exceeded your expense goal. Try these methods to cut down on unnecessary expenses:\n"
                    "- Review your monthly bills and negotiate for better rates on services like internet and insurance.\n"
                    "- Use cashback and discount apps to save money on everyday purchases.\n"
                    "- Set spending limits for discretionary categories, such as entertainment and dining out."
                )
            else:
                return (
                    "Good job! You are within your expense goal. Keep it up with these practices:\n"
                    "- Continue to monitor your expenses regularly to ensure they stay within budget.\n"
                    "- Build an emergency fund to cover unexpected expenses without derailing your budget.\n"
                    "- Set aside a portion of your income for future big purchases to avoid going into debt."
                )
        elif goal_type == 'Savings':
            if progress < goal_amount * 0.5:
                return (
                    "You are far from your savings goal. Consider these strategies to increase your savings rate:\n"
                    "- Automate your savings by setting up automatic transfers to your savings account.\n"
                    "- Cut down on non-essential expenses and redirect those funds into savings.\n"
                    "- Look for high-interest savings accounts or investment options to grow your savings faster."
                )
            elif progress < goal_amount:
                return (
                    "You are on track with your savings. Keep up the good work with these tips:\n"
                    "- Continue to save a fixed percentage of your income each month.\n"
                    "- Review your budget regularly to identify additional savings opportunities.\n"
                    "- Set specific short-term and long-term savings goals to stay motivated."
                )
            else:
                return (
                    "Congratulations! You've met your savings goal. Here are some next steps:\n"
                    "- Set new savings goals for future financial milestones, such as buying a home or retirement.\n"
                    "- Consider diversifying your savings into investments to potentially earn higher returns.\n"
                    "- Maintain an emergency fund to cover unexpected expenses and protect your financial stability."
                )
        elif goal_type == 'Investments':
            if progress < goal_amount * 0.5:
                return (
                    "You are far from your investment goal. Consider these strategies to boost your investments:\n"
                    "- Allocate a higher percentage of your income towards investments.\n"
                    "- Diversify your investment portfolio to spread risk and potentially increase returns.\n"
                    "- Research and invest in different asset classes, such as stocks, bonds, and real estate."
                )
            elif progress < goal_amount:
                return (
                    "You are on track with your investments. Keep it up with these tips:\n"
                    "- Continue to invest regularly, even if the amounts are small.\n"
                    "- Rebalance your portfolio periodically to maintain your desired asset allocation.\n"
                    "- Stay informed about market trends and adjust your investment strategy accordingly."
                )
            else:
                return (
                    "Congratulations! You've met your investment goal. Here are some next steps:\n"
                    "- Set new investment goals to continue growing your wealth.\n"
                    "- Explore different investment opportunities to diversify your portfolio further.\n"
                    "- Consider consulting with a financial advisor to optimize your investment strategy."
                )

    def get_goals_data(self):
        conn = sqlite3.connect('finance.db')
        c = conn.cursor()
        c.execute('SELECT goal_type, goal_category, goal_amount, progress FROM financial_goals')
        goals = c.fetchall()
        conn.close()
        return goals
