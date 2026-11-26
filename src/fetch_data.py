"""Unduh data QQQ, holdings, bobot sektor, dan harga holding terbesar dari Yahoo Finance."""
from datetime import date
from pathlib import Path

import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
TICKER = "QQQ"
PERIOD = "5y"
TOP_N = 10


def fetch_prices() -> pd.DataFrame:
    df = yf.download(TICKER, period=PERIOD, auto_adjust=False, progress=False)
    df.columns = df.columns.get_level_values(0)
    return df[["Open", "High", "Low", "Close", "Adj Close", "Volume"]].dropna()


def fetch_fund_info() -> tuple[pd.DataFrame, pd.Series, dict]:
    fund = yf.Ticker(TICKER)
    holdings = fund.funds_data.top_holdings.head(TOP_N).reset_index()
    sectors = pd.Series(fund.funds_data.sector_weightings, name="Bobot")
    info = {
        "nama": fund.info.get("longName"),
        "expense_ratio_persen": fund.info.get("netExpenseRatio"),
    }
    return holdings, sectors, info


def fetch_constituent_closes(symbols: list[str]) -> pd.DataFrame:
    df = yf.download(symbols, period=PERIOD, auto_adjust=False, progress=False)["Close"]
    return df[symbols].dropna()


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    prices = fetch_prices()
    holdings, sectors, info = fetch_fund_info()
    closes = fetch_constituent_closes(holdings["Symbol"].tolist())

    prices.to_csv(DATA_DIR / "qqq_ohlcv.csv")
    holdings.to_csv(DATA_DIR / "holdings_top.csv", index=False)
    sectors.to_csv(DATA_DIR / "sector_weights.csv", index_label="Sektor")
    closes.to_csv(DATA_DIR / "constituents_close.csv")
    asof = (
        f"diambil: {date.today().isoformat()}\n"
        f"data harga terakhir: {prices.index[-1].date().isoformat()}\n"
        f"nama: {info['nama']}\n"
        f"expense_ratio_persen: {info['expense_ratio_persen']}\n"
        "sumber: Yahoo Finance via yfinance\n"
    )
    (DATA_DIR / "ASOF.txt").write_text(asof)
    print(asof)


if __name__ == "__main__":
    main()
