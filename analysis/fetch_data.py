import asyncio #manages asynchronous coroutines (event loop, scheduling) 
import aiohttp #allows async HTTP requests, unlike requests (blocking)
from lxml import html # efficient C-based parser for HTML/XML documents
from collections import OrderedDict
from datetime import datetime
import time
import pandas as pd

TICKERS = ["BTC-USD", "ETH-USD", "SOL-USD", "ADA-USD", "XRP-USD"]
HEADERS = {"User-Agent": "Mozilla/5.0"}
POLL_INTERVAL = 4
TOTAL_DURATION = 60
OUTPUT_PATH = "../data/crypto_prices.csv"

class FetchData:
    def __init__(
        self,
        tickers=None,
        headers=None,
        poll_interval: int = POLL_INTERVAL,
        total_duration: int = TOTAL_DURATION,
        output_path: str = OUTPUT_PATH
    ):
        self.tickers = tickers or TICKERS
        self.headers = headers or HEADERS
        self.poll_interval = poll_interval
        self.total_duration = total_duration
        self.output_path = output_path

    async def fetch_price_json(self, session: aiohttp.ClientSession, ticker: str) -> float:
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

    async def fetch_price_html(self, session: aiohttp.ClientSession, ticker: str) -> float:
        url = f"https://finance.yahoo.com/quote/{ticker}/"
        async with session.get(url) as resp:
            resp.raise_for_status()
            tree = html.fromstring(await resp.text())
            nodes = tree.xpath('//span[@data-test="qsp-price"]/text()')
            if not nodes:
                raise ValueError(f"No HTML price element for {ticker}")
            return float(nodes[0].replace(",", ""))

    async def fetch_price(self, session: aiohttp.ClientSession, ticker: str) -> float:
        try:
            return await self.fetch_price_json(session, ticker)
        except Exception:
            return await self.fetch_price_html(session, ticker)

    async def collect_prices(self) -> OrderedDict:
        crypto_prices = OrderedDict((t, []) for t in self.tickers)
        start = time.time()

        async with aiohttp.ClientSession(headers=self.headers) as session:
            while time.time() - start < self.total_duration:
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                tasks = [self.fetch_price(session, t) for t in self.tickers]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                print(f"\nPrices at {ts}:")
                for ticker, res in zip(self.tickers, results):
                    if isinstance(res, Exception):
                        price = None
                        print(f"  ❌ {ticker}: failed ({res})")
                    else:
                        price = float(res)
                        print(f"   {ticker}: ${price:.2f}")
                    crypto_prices[ticker].append((ts, price))

                await asyncio.sleep(self.poll_interval)

        return crypto_prices

    def run(self):
        crypto_prices = asyncio.run(self.collect_prices())

        # flatten into records
        records = []
        for ticker, history in crypto_prices.items():
            for ts, price in history:
                records.append({"date": ts, "ticker": ticker, "price": price})

        df = pd.DataFrame(records, columns=["date", "ticker", "price"])
        df.to_csv(self.output_path, index=False)
        print(f"\nSaved {len(df)} rows to {self.output_path}")
        print(df)


if __name__ == "__main__":
    fetcher = FetchData()
    fetcher.run()
