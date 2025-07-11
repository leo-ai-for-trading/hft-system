import asyncio #manages asynchronous coroutines (event loop, scheduling) 
import aiohttp #allows async HTTP requests, unlike requests (blocking)
from lxml import html # efficient C-based parser for HTML/XML documents
from collections import OrderedDict
from datetime import datetime
import time
import pandas as pd

# ───── CONFIG ─────
TICKERS        = ["BTC-USD", "ETH-USD", "SOL-USD", "ADA-USD", "XRP-USD"]
HEADERS        = {"User-Agent": "Mozilla/5.0"}
POLL_INTERVAL  = 4      # seconds between polls
TOTAL_DURATION = 60     # total run time in seconds (1 minute)
OUTPUT_PATH    = "../data/crypto_prices.csv"
# ────────────────────────

async def fetch_price_json(session: aiohttp.ClientSession, ticker: str) -> float:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    params = {"range": "1d", "interval": "1m"}
    async with session.get(url, params=params) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)
        closes = data["chart"]["result"][0]["indicators"]["quote"][0]["close"]
        for px in reversed(closes):
            if px is not None:
                return float(px)
        raise ValueError(f"No valid close price in JSON for {ticker}")

async def fetch_price_html(session: aiohttp.ClientSession, ticker: str) -> float:
    url = f"https://finance.yahoo.com/quote/{ticker}/"
    async with session.get(url) as resp:
        resp.raise_for_status()
        tree = html.fromstring(await resp.text())
        nodes = tree.xpath('//span[@data-test="qsp-price"]/text()')
        if not nodes:
            raise ValueError(f"No HTML price element for {ticker}")
        # strip any commas before converting
        return float(nodes[0].replace(",", ""))

async def fetch_price(session: aiohttp.ClientSession, ticker: str) -> float:
    try:
        return await fetch_price_json(session, ticker)
    except Exception:
        return await fetch_price_html(session, ticker)

async def collect_prices():
    # OrderedDict mapping each ticker to a list of (timestamp, price)
    crypto_prices = OrderedDict((t, []) for t in TICKERS)
    start = time.time()

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        while time.time() - start < TOTAL_DURATION:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            tasks = [fetch_price(session, t) for t in TICKERS]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Print and store each price without thousands separators
            print(f"\nPrices at {ts}:")
            for ticker, res in zip(TICKERS, results):
                if isinstance(res, Exception):
                    price = None
                    print(f"  ❌ {ticker}: failed ({res})")
                else:
                    price = float(res)  # ensure type float
                    print(f"  📈 {ticker}: ${price:.2f}")
                crypto_prices[ticker].append((ts, price))

            await asyncio.sleep(POLL_INTERVAL)

    return crypto_prices

def main():
    crypto_prices = asyncio.run(collect_prices())

    # Flatten OrderedDict into a DataFrame
    records = []
    for ticker, history in crypto_prices.items():
        for ts, price in history:
            records.append({
                "date": ts,
                "ticker": ticker,
                "price": price
            })

    df = pd.DataFrame(records, columns=["date", "ticker", "price"])
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved {len(df)} rows to {OUTPUT_PATH}")
    print(df)

if __name__ == "__main__":
    main()







