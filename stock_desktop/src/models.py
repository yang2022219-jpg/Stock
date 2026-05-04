from dataclasses import dataclass


@dataclass
class TradeRecord:
    id: int | None
    symbol: str
    name: str
    trade_time: str
    side: str
    quantity: float
    price: float
    currency: str
    fee: float
    tax: float
    note: str
