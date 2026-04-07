"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

type Quote = {
  symbol: string;
  price: number;
  change: number;
  changePct: number;
  time: number;
  high: number;
  low: number;
  open: number;
  prevClose: number;
};

type QuoteApiResponse = {
  provider: string;
  symbols: Quote[];
};

function formatNumber(value: number) {
  return value.toFixed(2);
}

export default function HomePage() {
  const [quotes, setQuotes] = useState<Quote[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchQuotes = useCallback(async (isManual = false) => {
    if (isManual) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }

    setError(null);

    try {
      const response = await fetch("/api/quotes", { cache: "no-store" });
      const payload = (await response.json()) as QuoteApiResponse | { error?: string };

      if (!response.ok) {
        throw new Error(payload && "error" in payload ? payload.error ?? "Unknown error" : "Failed to load quotes");
      }

      setQuotes((payload as QuoteApiResponse).symbols);
    } catch (fetchError) {
      const message = fetchError instanceof Error ? fetchError.message : "Unknown error";
      setError(message);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    void fetchQuotes(false);
    const intervalId = setInterval(() => {
      void fetchQuotes(false);
    }, 5000);

    return () => clearInterval(intervalId);
  }, [fetchQuotes]);

  const updatedTime = useMemo(() => {
    if (quotes.length === 0) return "-";
    const latestUnix = Math.max(...quotes.map((quote) => quote.time));
    return new Date(latestUnix * 1000).toLocaleString();
  }, [quotes]);

  return (
    <main>
      <h1>Stock Real-time Dashboard</h1>
      <p>Tickers: TSLA / NVDA / AMD</p>

      <div className="status-row">
        <p>
          Updated time: <strong>{updatedTime}</strong>
        </p>
        <button type="button" onClick={() => void fetchQuotes(true)} disabled={loading || refreshing}>
          {refreshing ? "Refreshing..." : "Refresh now"}
        </button>
      </div>

      {loading && <p style={{ marginTop: 12 }}>Loading quotes...</p>}
      {error && <div className="error">Error: {error}</div>}

      <table>
        <thead>
          <tr>
            <th>Ticker</th>
            <th>Price</th>
            <th>Change</th>
            <th>Change%</th>
            <th>Open</th>
            <th>High</th>
            <th>Low</th>
            <th>Prev Close</th>
          </tr>
        </thead>
        <tbody>
          {quotes.map((quote) => (
            <tr key={quote.symbol}>
              <td>{quote.symbol}</td>
              <td>{formatNumber(quote.price)}</td>
              <td className={quote.change >= 0 ? "positive" : "negative"}>{formatNumber(quote.change)}</td>
              <td className={quote.changePct >= 0 ? "positive" : "negative"}>{formatNumber(quote.changePct)}%</td>
              <td>{formatNumber(quote.open)}</td>
              <td>{formatNumber(quote.high)}</td>
              <td>{formatNumber(quote.low)}</td>
              <td>{formatNumber(quote.prevClose)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
