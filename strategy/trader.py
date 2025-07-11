import time
import asyncio
import numpy as np
import pandas as pd

from analysis.fetch_data import FetchData
from strategy.template    import Graph

class Trading:
    def __init__(self,
                 tickers=None,
                 poll_interval: float = 4,
                 total_duration: float = 60):
        self.poll_interval  = poll_interval
        self.total_duration = total_duration
        self.fetcher = FetchData(
            tickers=tickers,
            poll_interval=poll_interval,
            total_duration=poll_interval  # one fetch per iteration
        )

    def get_price(self) -> pd.DataFrame:
        crypto_dict = asyncio.run(self.fetcher.collect_prices())
        records = []
        for symbol, history in crypto_dict.items():
            _, price = history[-1]
            records.append({"symbol": symbol, "price": price})
        return pd.DataFrame(records)

    def strategy(self):
        start_time = time.time()
        end_time   = start_time + self.total_duration

        iteration = 1
        while time.time() < end_time:
            loop_start = time.perf_counter()

            ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print(f"\n[{ts}] Iteration #{iteration} starting…")

            # 1) Fetch and prepare data
            df = self.get_price()
            df["weight"] = -np.log(df["price"].astype(float))

            # 2) Build graph
            g = Graph()
            for sym in df["symbol"]:
                g.add_node(sym)
            n = len(df)
            for i in range(n - 1):
                g.add_arc(df.symbol[i], df.symbol[i+1], df.weight[i])
            for i in reversed(range(n - 1)):
                g.add_arc(df.symbol[i], df.symbol[i+1], df.weight[i])

            # 3) Run Bellman-Ford
            dist, prec, has_cycle = g.bellman_ford(g.weight, 0)
            profit = np.exp(-sum(dist)) - 1

            # 4) Measure elapsed
            loop_end = time.perf_counter()
            elapsed = loop_end - loop_start

            # 5) Report result + performance
            status = (f"Arbitrage! Profit ≈ {profit*100:.2f}%"
                      if has_cycle else "No arbitrage")
            print(f"    → {status}")
            print(f"    → Iteration time: {elapsed*1000:.1f} ms")

            # exit early if found
            if has_cycle:
                return True, profit

            # wait until next iteration
            to_next = self.poll_interval - elapsed
            if to_next > 0:
                print(f"    → Sleeping {to_next:.2f}s before next run…")
                time.sleep(to_next)
            iteration += 1

        print(f"\n {self.total_duration}s elapsed, stopping—no arbitrage found.")
        return False, 0.0


if __name__ == "__main__":
    trader = Trading(
        tickers=["BTC-USD","ETH-USD","SOL-USD","ADA-USD","XRP-USD"],
        poll_interval=4,
        total_duration=60
    )
    trader.strategy()
