from collections import defaultdict


def calc_portfolio(trades, prices):
    price_map = {p["symbol"]: p for p in prices}

    hold_qty = defaultdict(float)
    hold_cost = defaultdict(float)
    realized = defaultdict(float)
    meta = {}

    for t in sorted(trades, key=lambda r: r["trade_time"]):
        symbol = t["symbol"]
        qty = float(t["quantity"])
        gross = qty * float(t["price"])
        extra_cost = float(t["fee"]) + float(t["tax"])
        total_value = gross + extra_cost
        meta[symbol] = {"name": t["name"], "currency": t["currency"]}

        if t["side"] == "BUY":
            hold_qty[symbol] += qty
            hold_cost[symbol] += total_value
        else:
            if hold_qty[symbol] <= 0:
                continue
            avg_cost = hold_cost[symbol] / hold_qty[symbol]
            sell_cost = avg_cost * qty
            proceeds = gross - extra_cost
            realized[symbol] += proceeds - sell_cost
            hold_qty[symbol] -= qty
            hold_cost[symbol] -= sell_cost

    holdings = []
    totals = {
        "cost": 0.0,
        "market_value": 0.0,
        "unrealized": 0.0,
        "realized": sum(realized.values()),
        "return_rate": 0.0,
    }

    for symbol, qty in hold_qty.items():
        if qty <= 0:
            continue
        info = meta[symbol]
        avg_cost = hold_cost[symbol] / qty
        m_price = price_map.get(symbol, {"current_price": 0})["current_price"]
        market_value = qty * float(m_price)
        unrealized = market_value - hold_cost[symbol]
        totals["cost"] += hold_cost[symbol]
        totals["market_value"] += market_value
        totals["unrealized"] += unrealized
        holdings.append(
            {
                "symbol": symbol,
                "name": info["name"],
                "currency": info["currency"],
                "quantity": qty,
                "avg_cost": avg_cost,
                "current_price": float(m_price),
                "cost": hold_cost[symbol],
                "market_value": market_value,
                "unrealized": unrealized,
                "realized": realized[symbol],
            }
        )

    if totals["cost"] > 0:
        totals["return_rate"] = (totals["unrealized"] + totals["realized"]) / totals["cost"] * 100

    return holdings, totals
