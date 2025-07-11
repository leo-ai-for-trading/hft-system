# HFT - System

## Crypto Price Collector

A Python script that periodically fetches cryptocurrency prices (BTC, ETH, SOL, ADA, XRP) from Yahoo Finance for a specified duration, prints them in real-time, and saves the historical data to a CSV file.

---

## Table of Contents

1. [Features](#features)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [How It Works](#how-it-works)

   * [Async Fetching](#async-fetching)
   * [JSON vs HTML Fallback](#json-vs-html-fallback)
   * [Data Collection](#data-collection)
   * [Data Export](#data-export)
7. [Output](#output)
8. [Customization](#customization)
9. [License](#license)

---

## Features

* **Asynchronous HTTP requests** using `aiohttp` for non-blocking performance.
* **Fast HTML parsing** with `lxml` when JSON endpoint fails.
* **Ordered history** storage in memory for each ticker.
* **Real-time console output** at configurable intervals.
* **Automatic CSV export** after a defined run duration.

---

## Requirements

* Python 3.8+
* Packages:

  * `aiohttp`
  * `lxml`
  * `pandas`

Install using pip:

```bash
pip install aiohttp lxml pandas
```

---

## Installation

1. Clone or download this repository.
2. Ensure you have Python 3.8 or later installed.
3. Install required packages (see [Requirements](#requirements)).

---

## Configuration

All configuration values are defined at the top of the script:

| Variable         | Description                                           | Default                       |
| ---------------- | ----------------------------------------------------- | ----------------------------- |
| `TICKERS`        | List of asset symbols to fetch (Yahoo Finance format) | `["BTC-USD", ...]`            |
| `HEADERS`        | HTTP headers to send with each request                | `{"User-Agent": ...}`         |
| `POLL_INTERVAL`  | Seconds to wait between fetches                       | `4`                           |
| `TOTAL_DURATION` | Total runtime in seconds                              | `60` (1 minute)               |
| `OUTPUT_PATH`    | CSV output file path                                  | `"../data/crypto_prices.csv"` |

Modify these values to suit your needs.

---

## Usage

Run the script directly:

```bash
python fetch_prices.py
```

The script will:

1. Fetch prices every `POLL_INTERVAL` seconds for `TOTAL_DURATION` seconds.
2. Print each round of prices in the console.
3. Save the collected data to `OUTPUT_PATH` as a CSV.

---

## How It Works

### Async Fetching

* Uses `asyncio` and `aiohttp` to send concurrent HTTP requests.
* Improves throughput when collecting multiple tickers.

### JSON vs HTML Fallback

1. **Primary**: Hits Yahoo’s undocumented JSON API (`/v8/finance/chart/{ticker}`) and extracts the last non-null close price.
2. **Fallback**: If JSON fails, scrapes the static HTML page for `<span data-test="qsp-price">` using `lxml`.

### Data Collection

* Maintains an `OrderedDict` mapping each ticker to a list of `(timestamp, price)` tuples.
* On each loop iteration, appends new data instead of overwriting.
* Prints formatted output to console.

### Data Export

* After the runtime elapses, flattens the `OrderedDict` to a Pandas DataFrame:

  * Columns: `date`, `ticker`, `price`.
* Saves to CSV at `OUTPUT_PATH`.

---

## Output

Example console output:

```
Prices at 2025-07-11 17:45:12:
  📈 BTC-USD: $117,502.62
  📈 ETH-USD: $2,979.22
  📈 SOL-USD: $24.17
  📈 ADA-USD: $0.50
  📈 XRP-USD: $2.93

Saved 75 rows to ../data/crypto_prices.csv
```

Sample CSV (`crypto_prices.csv`):

| date                | ticker  | price     |
| ------------------- | ------- | --------- |
| 2025-07-11 17:45:12 | BTC-USD | 117502.62 |
| 2025-07-11 17:45:12 | ETH-USD | 2979.22   |
| ...                 | ...     | ...       |

---

## Customization

* **Change tickers**: add or remove symbols in `TICKERS`.
* **Adjust interval/duration**: modify `POLL_INTERVAL` and `TOTAL_DURATION`.
* **Output format**: adjust DataFrame operations or path.
* **Error handling**: extend to retry or log failures separately.

---

## License

This project is released under the MIT License. Feel free to use and modify.
