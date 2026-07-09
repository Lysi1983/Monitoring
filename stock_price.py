#!/usr/bin/env python3
"""Fetch the latest price for a US stock ticker via Yahoo Finance.

Yahoo's chart endpoint returns an empty body without a browser-like
User-Agent header, so one is always sent.
"""

from __future__ import annotations

import json
import sys
from urllib.request import Request, urlopen

CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"


def _fetch(url: str) -> str:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=15) as response:
        return response.read().decode("utf-8")


def get_price(ticker: str) -> dict:
    ticker = ticker.upper()
    data = json.loads(_fetch(CHART_URL.format(ticker=ticker)))
    result = data.get("chart", {}).get("result")
    if not result:
        raise ValueError(f"No price found for ticker {ticker}")
    price = result[0].get("meta", {}).get("regularMarketPrice")
    if price is None:
        raise ValueError(f"No price found for ticker {ticker}")
    return {"ticker": ticker, "price": price}


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: stock_price.py <TICKER>", file=sys.stderr)
        return 2
    print(get_price(sys.argv[1]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
