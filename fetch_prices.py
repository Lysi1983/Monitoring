#!/usr/bin/env python3
"""Fetch today's stock/fund prices once and cache them to a JSON file.

Run each weekday morning by cron, a few minutes before the "Сутрешен
отчет за портфолио" cloud routine. The routine reads prices from
repository/prices/latest.json instead of calling stock_price.py /
isin_price.py itself for every ticker, so Yahoo/onemarkets are hit once
per morning instead of once per routine run.

Ticker/ISIN lists mirror the routine's stock and fund lists (see the
"Вечерен/Сутрешен отчет за портфолио" trigger). Update both places if
the user's holdings change.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone

sys.path.insert(0, "/home/ubuntu/MyProjects/Monitoring")

from isin_price import get_price as get_fund_price
from stock_price import get_price as get_stock_price

STOCK_TICKERS = ["SEDG", "LUMN", "BBAI", "QUBT", "VUAA.DE"]
FUND_ISINS = {
    "LU0568620560": "Amundi Cash",
    "LU2673943267": "BlackRock Low Duration",
    "LU2595024469": "Pimco Strategic Bond",
    "LU2595023222": "Pictet Balanced",
    "LU2503841905": "Fidelity Dividend Aristocrats",
    "LU2503836814": "BlackRock Global Equity",
    "LU2673954033": "Rockefeller Luxury Goods",
    "LU2595018065": "J.P. Morgan US",
    "LU2503834447": "J.P. Morgan Emerging Markets",
}
OUTPUT_PATH = "/home/ubuntu/MyProjects/Monitoring/repository/prices/latest.json"


def main() -> int:
    stocks = {}
    for ticker in STOCK_TICKERS:
        try:
            stocks[ticker] = get_stock_price(ticker)["price"]
        except Exception as e:
            print(f"SKIP stock {ticker}: {e}", file=sys.stderr)

    funds = {}
    for isin, name in FUND_ISINS.items():
        try:
            funds[isin] = get_fund_price(isin)["price"]
        except Exception as e:
            print(f"SKIP fund {isin} ({name}): {e}", file=sys.stderr)

    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stocks": stocks,
        "funds": funds,
    }

    with open(OUTPUT_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(stocks)} stock(s) and {len(funds)} fund(s) to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
