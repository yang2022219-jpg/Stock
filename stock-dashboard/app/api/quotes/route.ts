import { NextResponse } from "next/server";

const symbols = ["TSLA", "NVDA", "AMD"] as const;
const FINNHUB_BASE_URL = "https://finnhub.io/api/v1/quote";

type FinnhubQuoteResponse = {
  c: number;
  d: number;
  dp: number;
  h: number;
  l: number;
  o: number;
  pc: number;
  t: number;
};

export async function GET() {
  const apiKey = process.env.FINNHUB_API_KEY;

  if (!apiKey) {
    return NextResponse.json({ error: "Missing FINNHUB_API_KEY" }, { status: 500 });
  }

  try {
    const data = await Promise.all(
      symbols.map(async (symbol) => {
        const url = `${FINNHUB_BASE_URL}?symbol=${encodeURIComponent(symbol)}&token=${encodeURIComponent(apiKey)}`;
        const response = await fetch(url, { cache: "no-store" });

        if (!response.ok) {
          const detail = await response.text();
          throw new Error(`Finnhub request failed for ${symbol}: ${response.status} ${response.statusText} ${detail}`);
        }

        const quote = (await response.json()) as FinnhubQuoteResponse;

        return {
          symbol,
          price: quote.c,
          change: quote.d,
          changePct: quote.dp,
          time: quote.t,
          high: quote.h,
          low: quote.l,
          open: quote.o,
          prevClose: quote.pc
        };
      })
    );

    return NextResponse.json({ provider: "finnhub", symbols: data });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown provider error";
    return NextResponse.json({ error: `Failed to fetch quote data: ${message}` }, { status: 502 });
  }
}
