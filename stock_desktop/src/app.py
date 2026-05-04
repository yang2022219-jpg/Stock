from datetime import datetime
import csv
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from .db import Database
from .portfolio import calc_portfolio

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class StockApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("股票買賣紀錄系統")
        self.geometry("1280x800")

        self.db = Database()
        self.db.seed_demo_data()
        self.selected_trade_id = None

        self.build_ui()
        self.refresh_all()

    def build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.dashboard = ctk.CTkFrame(self)
        self.dashboard.grid(row=0, column=0, sticky="ew", padx=12, pady=8)
        self.metric_labels = {}
        for i, key in enumerate(["總成本", "總市值", "未實現損益", "已實現損益", "總報酬率"]):
            card = ctk.CTkFrame(self.dashboard)
            card.grid(row=0, column=i, padx=6, pady=6, sticky="ew")
            self.dashboard.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(card, text=key, font=("Microsoft JhengHei", 14, "bold")).pack(pady=(8, 0))
            lbl = ctk.CTkLabel(card, text="-", font=("Consolas", 18))
            lbl.pack(pady=(4, 8))
            self.metric_labels[key] = lbl

        notebook = ttk.Notebook(self)
        notebook.grid(row=1, column=0, sticky="nsew", padx=12, pady=8)

        self.trade_tab = ctk.CTkFrame(notebook)
        self.price_tab = ctk.CTkFrame(notebook)
        self.analysis_tab = ctk.CTkFrame(notebook)

        notebook.add(self.trade_tab, text="交易紀錄")
        notebook.add(self.price_tab, text="現價管理")
        notebook.add(self.analysis_tab, text="持股分析")

        self.build_trade_tab()
        self.build_price_tab()
        self.build_analysis_tab()

    def build_trade_tab(self):
        form = ctk.CTkFrame(self.trade_tab)
        form.pack(fill="x", padx=8, pady=8)
        fields = ["symbol", "name", "trade_time", "side", "quantity", "price", "currency", "fee", "tax", "note"]
        self.trade_inputs = {}
        for i, f in enumerate(fields):
            ctk.CTkLabel(form, text=f).grid(row=i // 5 * 2, column=(i % 5) * 2, padx=4, pady=2, sticky="w")
            if f in ["side", "currency"]:
                combo = ttk.Combobox(form, values=["BUY", "SELL"] if f == "side" else ["USD", "TWD"], width=10)
                combo.grid(row=i // 5 * 2 + 1, column=(i % 5) * 2, padx=4, pady=2)
                self.trade_inputs[f] = combo
            else:
                ent = ctk.CTkEntry(form, width=130)
                ent.grid(row=i // 5 * 2 + 1, column=(i % 5) * 2, padx=4, pady=2)
                self.trade_inputs[f] = ent

        self.trade_inputs["trade_time"].insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.trade_inputs["side"].set("BUY")
        self.trade_inputs["currency"].set("USD")

        btns = ctk.CTkFrame(self.trade_tab)
        btns.pack(fill="x", padx=8, pady=4)
        ctk.CTkButton(btns, text="新增", command=self.add_trade).pack(side="left", padx=4)
        ctk.CTkButton(btns, text="更新", command=self.update_trade).pack(side="left", padx=4)
        ctk.CTkButton(btns, text="刪除", fg_color="#CC3333", command=self.delete_trade).pack(side="left", padx=4)
        ctk.CTkButton(btns, text="匯出CSV", command=self.export_trades_csv).pack(side="right", padx=4)

        columns = ("id", "symbol", "name", "trade_time", "side", "quantity", "price", "currency", "fee", "tax", "note")
        self.trade_tree = ttk.Treeview(self.trade_tab, columns=columns, show="headings", height=16)
        for col in columns:
            self.trade_tree.heading(col, text=col)
            self.trade_tree.column(col, width=100)
        self.trade_tree.column("note", width=180)
        self.trade_tree.pack(fill="both", expand=True, padx=8, pady=8)
        self.trade_tree.bind("<<TreeviewSelect>>", self.on_trade_select)

    def build_price_tab(self):
        top = ctk.CTkFrame(self.price_tab)
        top.pack(fill="x", padx=8, pady=8)
        self.price_symbol = ctk.CTkEntry(top, placeholder_text="symbol")
        self.price_name = ctk.CTkEntry(top, placeholder_text="name")
        self.price_currency = ttk.Combobox(top, values=["USD", "TWD"], width=8)
        self.price_currency.set("USD")
        self.price_value = ctk.CTkEntry(top, placeholder_text="current price")

        for w in [self.price_symbol, self.price_name, self.price_currency, self.price_value]:
            w.pack(side="left", padx=4)

        ctk.CTkButton(top, text="儲存/更新現價", command=self.save_price).pack(side="left", padx=8)
        ctk.CTkButton(top, text="匯出持股分析CSV", command=self.export_analysis_csv).pack(side="right", padx=4)

        cols = ("symbol", "name", "currency", "current_price", "updated_at")
        self.price_tree = ttk.Treeview(self.price_tab, columns=cols, show="headings", height=18)
        for col in cols:
            self.price_tree.heading(col, text=col)
            self.price_tree.column(col, width=150)
        self.price_tree.pack(fill="both", expand=True, padx=8, pady=8)

    def build_analysis_tab(self):
        self.analysis_tree = ttk.Treeview(
            self.analysis_tab,
            columns=("symbol", "name", "qty", "avg_cost", "current", "cost", "market", "unrealized", "realized"),
            show="headings",
            height=10,
        )
        for c in self.analysis_tree["columns"]:
            self.analysis_tree.heading(c, text=c)
            self.analysis_tree.column(c, width=110)
        self.analysis_tree.pack(fill="x", padx=8, pady=8)

        graph_frame = ctk.CTkFrame(self.analysis_tab)
        graph_frame.pack(fill="both", expand=True, padx=8, pady=8)

        self.fig = Figure(figsize=(10, 4), dpi=100)
        self.pie_ax = self.fig.add_subplot(121)
        self.bar_ax = self.fig.add_subplot(122)
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def add_trade(self):
        row = self.read_trade_form()
        if not row:
            return
        self.db.insert_trade(row)
        self.refresh_all()

    def update_trade(self):
        if not self.selected_trade_id:
            messagebox.showwarning("提醒", "請先選擇紀錄")
            return
        row = self.read_trade_form()
        if row:
            self.db.update_trade(self.selected_trade_id, row)
            self.refresh_all()

    def delete_trade(self):
        if not self.selected_trade_id:
            messagebox.showwarning("提醒", "請先選擇紀錄")
            return
        self.db.delete_trade(self.selected_trade_id)
        self.selected_trade_id = None
        self.refresh_all()

    def read_trade_form(self):
        try:
            row = (
                self.trade_inputs["symbol"].get().strip().upper(),
                self.trade_inputs["name"].get().strip(),
                self.trade_inputs["trade_time"].get().strip(),
                self.trade_inputs["side"].get().strip(),
                float(self.trade_inputs["quantity"].get().strip()),
                float(self.trade_inputs["price"].get().strip()),
                self.trade_inputs["currency"].get().strip(),
                float(self.trade_inputs["fee"].get().strip() or 0),
                float(self.trade_inputs["tax"].get().strip() or 0),
                self.trade_inputs["note"].get().strip(),
            )
            if not row[0] or not row[1]:
                raise ValueError
            return row
        except ValueError:
            messagebox.showerror("輸入錯誤", "請確認欄位與數字格式")
            return None

    def on_trade_select(self, _event):
        selected = self.trade_tree.selection()
        if not selected:
            return
        values = self.trade_tree.item(selected[0], "values")
        self.selected_trade_id = int(values[0])
        keys = ["symbol", "name", "trade_time", "side", "quantity", "price", "currency", "fee", "tax", "note"]
        for i, k in enumerate(keys, start=1):
            widget = self.trade_inputs[k]
            if isinstance(widget, ttk.Combobox):
                widget.set(values[i])
            else:
                widget.delete(0, tk.END)
                widget.insert(0, values[i])

    def save_price(self):
        try:
            self.db.upsert_price(
                self.price_symbol.get().strip().upper(),
                self.price_name.get().strip(),
                self.price_currency.get().strip(),
                float(self.price_value.get().strip()),
                datetime.now().strftime("%Y-%m-%d %H:%M"),
            )
            self.refresh_all()
        except ValueError:
            messagebox.showerror("輸入錯誤", "請輸入正確現價")

    def export_trades_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not path:
            return
        rows = self.db.fetch_trades()
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(rows[0].keys() if rows else [])
            for r in rows:
                writer.writerow(list(r))

    def export_analysis_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not path:
            return
        trades = self.db.fetch_trades()
        prices = self.db.fetch_prices()
        holdings, totals = calc_portfolio(trades, prices)
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["symbol", "name", "qty", "avg_cost", "current", "cost", "market", "unrealized", "realized"])
            for h in holdings:
                writer.writerow([h["symbol"], h["name"], h["quantity"], h["avg_cost"], h["current_price"], h["cost"], h["market_value"], h["unrealized"], h["realized"]])
            writer.writerow([])
            writer.writerow(["totals", totals["cost"], totals["market_value"], totals["unrealized"], totals["realized"], totals["return_rate"]])

    def refresh_all(self):
        self.refresh_trades()
        self.refresh_prices()
        self.refresh_analysis()

    def refresh_trades(self):
        for i in self.trade_tree.get_children():
            self.trade_tree.delete(i)
        for row in self.db.fetch_trades():
            self.trade_tree.insert("", "end", values=list(row))

    def refresh_prices(self):
        for i in self.price_tree.get_children():
            self.price_tree.delete(i)
        for row in self.db.fetch_prices():
            self.price_tree.insert("", "end", values=list(row))

    def refresh_analysis(self):
        trades = self.db.fetch_trades()
        prices = self.db.fetch_prices()
        holdings, totals = calc_portfolio(trades, prices)

        for i in self.analysis_tree.get_children():
            self.analysis_tree.delete(i)
        for h in holdings:
            self.analysis_tree.insert(
                "",
                "end",
                values=(h["symbol"], h["name"], h["quantity"], round(h["avg_cost"], 2), h["current_price"], round(h["cost"], 2), round(h["market_value"], 2), round(h["unrealized"], 2), round(h["realized"], 2)),
            )

        self.metric_labels["總成本"].configure(text=f"{totals['cost']:.2f}")
        self.metric_labels["總市值"].configure(text=f"{totals['market_value']:.2f}")
        self.metric_labels["未實現損益"].configure(text=f"{totals['unrealized']:.2f}")
        self.metric_labels["已實現損益"].configure(text=f"{totals['realized']:.2f}")
        self.metric_labels["總報酬率"].configure(text=f"{totals['return_rate']:.2f}%")

        self.pie_ax.clear()
        self.bar_ax.clear()
        labels = [f"{h['symbol']}" for h in holdings]
        values = [h["market_value"] for h in holdings]
        if values and sum(values) > 0:
            self.pie_ax.pie(values, labels=labels, autopct="%1.1f%%")
            self.pie_ax.set_title("持股占比圓餅圖")
            self.bar_ax.bar(labels, values)
            self.bar_ax.set_title("持股市值長條圖")
            self.bar_ax.set_ylabel("Market Value")
        self.canvas.draw()
