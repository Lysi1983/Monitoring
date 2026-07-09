#!/usr/bin/env python3
"""Fetch the latest price for an ISIN.

Tries the onemarkets.bg chart data feed first (covers onemarkets-branded
funds), then falls back to the Amundi fund search API (covers Amundi funds,
e.g. Amundi Cash, which aren't on the onemarkets platform).
"""

from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from urllib.parse import urlencode
from urllib.request import Request, urlopen

CHARTDATA_URL = "https://www.onemarkets.bg/bin/onemarkets-relaunch/multi-chartdata.csv"
AMUNDI_SEARCH_URL = (
    "https://www.amundi.bg/product-services/tip/shares/v2/categories/public/search.json"
)


def _fetch(url: str) -> str:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=15) as response:
        return response.read().decode("utf-8")


def _onemarkets_price(isin: str) -> float | None:
    day = (date.today() - timedelta(days=2)).strftime("%Y%m%d")
    url = (
        f"{CHARTDATA_URL}?isin={isin}&underlyings=&underlyingsIds=&start={day}"
        f"&end={day}&extras=&exchange=&tradingStartTime=00:00&tradingEndTime=23:59"
        "&underlyingCurrency="
    )
    records = [r for r in _fetch(url).split() if r.strip(";")]
    if not records:
        return None
    _, price, *_ = records[-1].split(";")
    return float(price)


def _amundi_price(isin: str) -> float | None:
    params = {
        "limit": 20,
        "page": 1,
        "sort[0][field]": "label",
        "sort[0][order]": "ASC",
        "perimeter": 168,
        "searchText": isin,
        "offset": 0,
        "grouping": "false",
        "category": "public",
        "partnerId": 768,
        "locale": "bg-BG",
        "id": 368,
    }
    url = f"{AMUNDI_SEARCH_URL}?{urlencode(params)}"
    data = json.loads(_fetch(url))
    docs = data.get("data", {}).get("response", {}).get("docs", [])
    for doc in docs:
        if doc.get("isin") == isin:
            return doc["lastNav"]["value"]
    return None


def get_price(isin: str) -> dict:
    price = _onemarkets_price(isin)
    if price is None:
        price = _amundi_price(isin)
    if price is None:
        raise ValueError(f"No price found for ISIN {isin}")
    return {"isin": isin, "price": price}


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: isin_price.py <ISIN>", file=sys.stderr)
        return 2
    print(get_price(sys.argv[1]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
