import tkinter as tk
from tkinter import ttk, scrolledtext, Toplevel
import sqlite3
import yfinance as yf
import datetime as dt
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import requests

NEWS_API_KEY = '97fa52573e0f444a99b479aa35430ab7'

class InvestmentTab:
    def __init__(self, parent):
        self.parent = parent

        # Create a Canvas for scrollable content
        self.canvas = tk.Canvas(self.parent)
        self.scrollableFrame = ttk.Frame(self.canvas)

        # Create a scrollbar linked to the canvas
        self.scrollbar = ttk.Scrollbar(self.parent, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Create a window within the canvas for the scrollable frame
        self.canvas.create_window((0, 0), window=self.scrollableFrame, anchor="nw")

        # Make the frame auto-expand
        self.scrollableFrame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.scrollableFrame.columnconfigure(0, weight=1)
        self.scrollableFrame.columnconfigure(1, weight=3)
        self.scrollableFrame.rowconfigure(0, weight=1)
        self.scrollableFrame.rowconfigure(1, weight=1)
        self.scrollableFrame.rowconfigure(2, weight=3)
        self.scrollableFrame.rowconfigure(3, weight=1)

        self.leftFrame = ttk.LabelFrame(self.scrollableFrame, text="Add Investment", style="primary.TLabelframe")
        self.leftFrame.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nsew")

        self.tickerLabel = ttk.Label(self.leftFrame, text="Ticker:")
        self.tickerLabel.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.tickerEntry = ttk.Entry(self.leftFrame)
        self.tickerEntry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.sharesLabel = ttk.Label(self.leftFrame, text="Shares:")
        self.sharesLabel.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.sharesEntry = ttk.Entry(self.leftFrame)
        self.sharesEntry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.priceLabel = ttk.Label(self.leftFrame, text="Purchase Price:")
        self.priceLabel.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.priceEntry = ttk.Entry(self.leftFrame)
        self.priceEntry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        self.dateLabel = ttk.Label(self.leftFrame, text="Purchase Date:")
        self.dateLabel.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.dateEntry = ttk.Entry(self.leftFrame)
        self.dateEntry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        self.addButton = ttk.Button(self.leftFrame, text="Add Investment", command=self.addInvestment)
        self.addButton.grid(row=4, column=0, columnspan=2, padx=5, pady=10)

        self.rightFrame = ttk.Frame(self.scrollableFrame, style="TFrame")
        self.rightFrame.grid(row=0, column=1, rowspan=4, padx=10, pady=10, sticky="nsew")

        self.rightFrame.rowconfigure(0, weight=1)
        self.rightFrame.rowconfigure(1, weight=1)
        self.rightFrame.rowconfigure(2, weight=1)
        self.rightFrame.rowconfigure(3, weight=3)

        self.investmentData = self.getInvestmentData()

        self.createAnalyticsView()
        self.createSummaryView()
        self.createNewsView()
        self.createDividendCalculator()

    def addInvestment(self):
        try:
            ticker = self.tickerEntry.get().upper()
            shares = float(self.sharesEntry.get())
            purchasePrice = float(self.priceEntry.get())
            purchaseDate = self.dateEntry.get()
            self.saveInvestmentToDb(ticker, shares, purchasePrice, purchaseDate)
            self.investmentData = self.getInvestmentData()
            self.updateAnalyticsView()
            self.updateSummaryView()
            self.updateNewsView()
            self.updateDividendCalculator()
        except ValueError:
            pass

    def createAnalyticsView(self):
        self.analyticsLabel = ttk.Label(self.rightFrame, text="Investment Analytics", style="primary.TLabel")
        self.analyticsLabel.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.analyticsText = scrolledtext.ScrolledText(self.rightFrame, wrap=tk.WORD, font=('Verdana', 10))
        self.analyticsText.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        self.updateAnalyticsView()

    def updateAnalyticsView(self):
        self.analyticsText.delete('1.0', tk.END)
        for stock in self.investmentData:
            ticker, shares, purchasePrice, purchaseDate = stock
            data, info = getStockData(ticker, purchaseDate)
            if data is not None and info is not None:
                metrics = calculateMetrics(ticker, data, info, shares, purchasePrice, purchaseDate)
                self.analyticsText.insert(tk.END, f"\nMetrics for {ticker}:\n")
                for metric, value in metrics.items():
                    self.analyticsText.insert(tk.END, f"{metric}: {value}\n")
                plotButton = ttk.Button(
                    self.analyticsText,
                    text='Plot Data',
                    command=lambda t=ticker: self.plotStockData(t))
                self.analyticsText.window_create(tk.END, window=plotButton)
                self.analyticsText.insert(tk.END, '\n')
            else:
                self.analyticsText.insert(tk.END, f"\nNo data available for {ticker}.\n")

    def createSummaryView(self):
        self.summaryLabel = ttk.Label(self.rightFrame, text="Investment Summary", style="primary.TLabel")
        self.summaryLabel.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        self.summaryText = scrolledtext.ScrolledText(self.rightFrame, wrap=tk.WORD, font=('Verdana', 10), height=5)
        self.summaryText.grid(row=3, column=0, padx=5, pady=5, sticky="nsew")

        self.updateSummaryView()

    def updateSummaryView(self):
        self.summaryText.delete('1.0', tk.END)
        totalInvested, totalPl = self.calculateSummary()
        self.summaryText.insert(tk.END, f"Total Invested: ${totalInvested:.2f}\n")
        self.summaryText.insert(tk.END, f"Total Profit/Loss: ${totalPl:.2f}\n")

    def createNewsView(self):
        self.newsLabel = ttk.Label(self.rightFrame, text="Financial News", style="primary.TLabel")
        self.newsLabel.grid(row=4, column=0, padx=5, pady=5, sticky="ew")

        self.newsFrame = ttk.Frame(self.rightFrame)
        self.newsFrame.grid(row=5, column=0, padx=5, pady=5, sticky="nsew")

        self.updateNewsView()

    def updateNewsView(self):
        for widget in self.newsFrame.winfo_children():
            widget.destroy()

        stocks = self.getInvestmentData()
        for stock in stocks:
            ticker, _, _, _ = stock
            tickerButton = ttk.Button(
                self.newsFrame,
                text=f"News for {ticker}",
                command=lambda t=ticker: self.showStockNews(t))
            tickerButton.pack(fill=tk.X, padx=10, pady=5)

    def plotStockData(self, ticker):
        def fetchAndPlot():
            startDate = startDateEntry.get()
            endDate = endDateEntry.get()

            data, _ = getStockData(ticker, startDate, endDate)
            if data is not None:
                ax.clear()
                ax.plot(data.index, data['Close'])
                ax.setTitle(f"{ticker} Stock Price")
                ax.setXlabel("Date")
                ax.setYlabel("Close Price (USD)")

                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%y'))
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right", fontsize=10)

                canvas.draw()

        topLevel = Toplevel(self.parent)
        topLevel.title(f"Stock Data for {ticker}")

        tk.Label(topLevel, text="Start Date (YYYY-MM-DD):").pack()
        startDateEntry = tk.Entry(topLevel)
        startDateEntry.pack()
        startDateEntry.insert(0, "2020-01-01")

        tk.Label(topLevel, text="End Date (YYYY-MM-DD):").pack()
        endDateEntry = tk.Entry(topLevel)
        endDateEntry.pack()
        endDateEntry.insert(0, dt.datetime.now().strftime("%Y-%m-%d"))

        plotButton = ttk.Button(topLevel, text="Plot Data", command=fetchAndPlot)
        plotButton.pack()

        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)

        canvas = FigureCanvasTkAgg(fig, master=topLevel)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

    def showStockNews(self, ticker):
        newsWindow = Toplevel(self.parent)
        newsWindow.title(f"News for {ticker}")
        newsWindow.geometry("800x600")

        newsText = scrolledtext.ScrolledText(newsWindow, wrap=tk.WORD, font=('Verdana', 10))
        newsText.pack(expand=True, fill='both', padx=10, pady=5)

        articles = fetchNews(ticker)
        if articles:
            for article in articles:
                newsText.insert(tk.END, f"Title: {article['title']}\n")
                newsText.insert(tk.END, f"Description: {article['description']}\n")
                newsText.insert(tk.END, f"URL: {article['url']}\n\n")
        else:
            newsText.insert(tk.END, f"No news available for {ticker}.\n")

        backButton = ttk.Button(newsWindow, text="Back", command=newsWindow.destroy)
        backButton.pack(side=tk.BOTTOM, padx=10, pady=10)

    def createDividendCalculator(self):
        calculatorFrame = ttk.LabelFrame(self.scrollableFrame, text="Dividend Calculator", style="primary.TLabelframe")
        calculatorFrame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        ttk.Label(calculatorFrame, text="Ticker:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.dividendTickerEntry = ttk.Entry(calculatorFrame)
        self.dividendTickerEntry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(calculatorFrame, text="Investment Amount:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.investmentAmountEntry = ttk.Entry(calculatorFrame)
        self.investmentAmountEntry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.calculateDividendButton = ttk.Button(calculatorFrame, text="Calculate Dividend", command=self.calculateDividend)
        self.calculateDividendButton.grid(row=2, column=0, columnspan=2, padx=5, pady=10)

        self.dividendResultLabel = ttk.Label(calculatorFrame, text="", style="primary.TLabel")
        self.dividendResultLabel.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

    def calculateDividend(self):
        try:
            ticker = self.dividendTickerEntry.get().upper()
            investmentAmount = float(self.investmentAmountEntry.get())
            data, info = getStockData(ticker)
            if data is not None and info is not None:
                dividendYield = info.get('dividendYield', 0)
                if dividendYield:
                    annualDividend = investmentAmount * dividendYield
                    quarterlyDividend = annualDividend / 4
                    self.dividendResultLabel.config(text=f"Expected Quarterly Dividend Amount: ${quarterlyDividend:.2f}")
                else:
                    self.dividendResultLabel.config(text="No dividend yield information available.")
            else:
                self.dividendResultLabel.config(text="Invalid ticker or no data available.")
        except ValueError:
            self.dividendResultLabel.config(text="Invalid input. Please enter numeric values.")

    def saveInvestmentToDb(self, ticker, shares, purchasePrice, purchaseDate):
        conn = sqlite3.connect('finance.db')
        c = conn.cursor()
        c.execute('INSERT INTO investments (ticker, shares, purchase_price, purchase_date) VALUES (?, ?, ?, ?)',
                  (ticker, shares, purchasePrice, purchaseDate))
        conn.commit()
        conn.close()

    def getInvestmentData(self):
        conn = sqlite3.connect('finance.db')
        c = conn.cursor()
        c.execute('SELECT ticker, shares, purchase_price, purchase_date FROM investments')
        data = c.fetchall()
        conn.close()
        return data

    def sellStock(self, ticker, sellPrice):
        conn = sqlite3.connect('finance.db')
        c = conn.cursor()
        c.execute('SELECT shares, purchase_price FROM investments WHERE ticker = ?', (ticker,))
        stock = c.fetchone()
        if stock:
            shares, purchasePrice = stock
            profitLoss = (sellPrice - purchasePrice) * shares
            c.execute('DELETE FROM investments WHERE ticker = ?', (ticker,))
            c.execute('INSERT INTO sales (ticker, shares, purchase_price, sell_price, profit_loss) VALUES (?, ?, ?, ?, ?)',
                      (ticker, shares, purchasePrice, sellPrice, profitLoss))
            conn.commit()
        conn.close()
        self.investmentData = self.getInvestmentData()
        self.updateAnalyticsView()
        self.updateSummaryView()

    def calculateSummary(self):
        totalInvested = 0
        totalPl = 0
        for stock in self.investmentData:
            ticker, shares, purchasePrice, purchaseDate = stock
            data, _ = getStockData(ticker, purchaseDate)
            if data is not None:
                currentPrice = data['Close'].iloc[-1]
                totalInvested += purchasePrice * shares
                totalPl += (currentPrice - purchasePrice) * shares
        return totalInvested, totalPl

def getStockData(ticker, startDate='2020-01-01', endDate=None):
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(start=startDate, end=endDate)
        return data, stock.info
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None, None

def calculateMetrics(ticker, data, info, shares, purchasePrice, purchaseDate):
    currentPrice = data['Close'].iloc[-1]
    previousClose = info.get('previousClose', 'N/A')
    openPrice = info.get('open', 'N/A')
    bid = info.get('bid', 'N/A')
    ask = info.get('ask', 'N/A')
    dayRange = formatRange(info.get('dayLow'), info.get('dayHigh'))
    fiftyTwoWeekRange = formatRange(info.get('fiftyTwoWeekLow'), info.get('fiftyTwoWeekHigh'))
    volume = info.get('volume', 'N/A')
    avgVolume = info.get('averageVolume', 'N/A')
    marketCap = info.get('marketCap', 'N/A')
    beta = info.get('beta', 'N/A')
    peRatio = info.get('trailingPE', 'N/A')
    eps = info.get('trailingEps', 'N/A')
    earningsDate = info.get('earningsDate', 'N/A')
    forwardDividendYield = f"{info.get('dividendRate', 'N/A')} ({info.get('dividendYield', 'N/A')})"
    exDividendDate = info.get('exDividendDate', 'N/A')
    oneYearTarget = info.get('targetMeanPrice', 'N/A')
    analystRating = info.get('recommendationKey', 'N/A')

    purchaseValue = purchasePrice * shares
    currentValue = currentPrice * shares
    openPl = currentValue - purchaseValue
    openPlPercent = (openPl / purchasePrice) * 100 if purchaseValue != 0 else 'N/A'
    dailyPl = (currentPrice - previousClose) * shares if previousClose != 'N/A' else 'N/A'
    dailyPlPercent = (dailyPl / (previousClose * shares)) * 100 if previousClose != 'N/A' and previousClose != 0 else 'N/A'
    daysHeld = (dt.datetime.now() - dt.datetime.strptime(purchaseDate, '%Y-%m-%d')).days
    annualReturn = ((currentPrice / purchasePrice) ** (365 / daysHeld) - 1) * 100 if daysHeld > 0 else 0

    return {
        'Ticker': ticker,
        'Shares': shares,
        'Purchase Price': f'${purchasePrice:.2f}',
        'Current Price': f'${currentPrice:.2f}',
        'Purchase Value': f'${purchaseValue:.2f}',
        'Current Value': f'${currentValue:.2f}',
        'Open P/L': f'${openPl:.2f} ({openPlPercent:.2f}%)',
        'Daily P/L': f'${dailyPl:.2f} ({dailyPlPercent:.2f}%)' if dailyPl != 'N/A' else 'N/A',
        'Annual Return (%)': f'{annualReturn:.2f}%',
        'Previous Close': previousClose,
        'Open': openPrice,
        'Bid': bid,
        'Ask': ask,
        'Day\'s Range': dayRange,
        '52 Week Range': fiftyTwoWeekRange,
        'Volume': volume,
        'Avg. Volume': avgVolume,
        'Market Cap': marketCap,
        'Beta (5Y Monthly)': beta,
        'PE Ratio (TTM)': peRatio,
        'EPS (TTM)': eps,
        'Earnings Date': earningsDate,
        'Forward Dividend & Yield': forwardDividendYield,
        'Ex-Dividend Date': exDividendDate,
        '1y Target Est': oneYearTarget,
        'Analyst Rating': analystRating
    }

def formatRange(low, high):
    return f'{low:.2f} - {high:.2f}' if low is not None and high is not None else 'N/A'

def fetchNews(ticker):
    url = f'https://newsapi.org/v2/everything?q={ticker}&apiKey={NEWS_API_KEY}'
    try:
        response = requests.get(url)
        response.raise_for_status()  # This will raise an HTTPError for bad responses (4xx and 5xx)
        return response.json().get('articles', [])
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Python 3.6+
    except Exception as err:
        print(f"Other error occurred: {err}")  # Python 3.6+
    return []