# stock-dashboard

即時股票報價 Dashboard（TSLA / NVDA / AMD），使用 Next.js App Router + TypeScript。

## 1) 本機執行

```bash
npm install
npm run dev
```

啟動後開啟 <http://localhost:3000>。

## 2) 設定環境變數 FINNHUB_API_KEY

1. 複製範例檔：

   ```bash
   cp .env.local.example .env.local
   ```

2. 編輯 `.env.local`，填入你的 key：

   ```env
   FINNHUB_API_KEY=YOUR_REAL_FINNHUB_API_KEY
   ```

3. 重新啟動開發伺服器。

## 3) 部署到 Vercel

1. 將此專案推到 GitHub。
2. 到 Vercel 按 **Add New... → Project**，選擇該 GitHub repo。
3. 在專案設定的 **Environment Variables** 新增：
   - Name: `FINNHUB_API_KEY`
   - Value: 你的 Finnhub API key
   - Environment: 至少勾選 `Production`（建議 `Preview` / `Development` 也設）
4. 按 **Deploy**。
5. 部署完成後，進入網站即可看到即時報價，每 5 秒自動刷新，也可按 **Refresh now** 手動刷新。
