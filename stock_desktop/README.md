# Windows 桌面版股票買賣紀錄軟體（Python + SQLite）

## 功能
- 新增 / 編輯 / 刪除交易紀錄
- 交易欄位：代號、名稱、交易時間、買賣別、股數、單價、USD/TWD、手續費、交易稅、備註
- 手動輸入現價
- 平均成本法計算已實現/未實現損益
- Dashboard 顯示總成本、總市值、總報酬
- 持股圓餅圖 + 長條圖
- SQLite 儲存
- 匯出交易紀錄與持股分析 CSV
- 內建測試資料

## 專案結構
```
stock_desktop/
├─ main.py
├─ requirements.txt
├─ stock_portfolio.db  # 啟動後自動建立
└─ src/
   ├─ __init__.py
   ├─ app.py
   ├─ db.py
   ├─ models.py
   └─ portfolio.py
```

## 在 PyCharm 執行
1. 用 PyCharm 開啟 `stock_desktop` 資料夾。
2. 建立虛擬環境（Python 3.11+ 建議）。
3. 安裝套件：
   ```bash
   pip install -r requirements.txt
   ```
4. 執行：
   ```bash
   python main.py
   ```

## 打包成 exe（Windows）
1. 安裝 PyInstaller：
   ```bash
   pip install pyinstaller
   ```
2. 在 `stock_desktop` 目錄執行：
   ```bash
   pyinstaller --noconfirm --onefile --windowed --name StockDesktop main.py
   ```
3. 產出檔案在 `dist/StockDesktop.exe`。
4. 若要保留資料庫在程式旁，建議改成：
   - 啟動程式時將資料庫放在 `Path.cwd()` 或 `%APPDATA%`。
   - 或使用 `--onedir` 模式方便攜帶附加檔案。
