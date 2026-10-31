import pandas as pd
import yfinance as yf

from src import config

def download_prices(tickers, start, end=None) -> pd.DataFrame: # Download adjusted close prices
    raw = yf.download(
        tickers, start=start, end=end,
        auto_adjust=True,
        progress=False,
    )
    prices = raw["Close"].copy()
    if prices.index.tz is not None:
        prices.index = prices.index.tz_localize(None)
    return prices.sort_index()

def validate_prices(prices: pd.DataFrame, jump_threshold: float = 0.15) -> pd.DataFrame: # per-ticker data quality
    daily_move = prices.pct_change(fill_method=None).abs()
    report = pd.DataFrame({
        "first_date": prices.apply(lambda s: s.first_valid_index()),
        "last_date": prices.apply(lambda s: s.last_valid_index()),
        "n_obs": prices.count(),
        "missing_pct": prices.isna().mean() * 100,
        "max_abs_daily_move_pct": daily_move.max() * 100,
        "n_jumps_over_threshold": (daily_move > jump_threshold).sum(),
    })
    return report.round(2).sort_values("missing_pct", ascending=False)

def clean_prices(prices: pd.DataFrame, max_missing_pct: float = 5.0, ffill_limit: int = 3) -> pd.DataFrame: # drop unusable tickers, fill gaps and align all series to common dates
    prices = prices.dropna(axis=1, how="all")                      
    bad = prices.columns[prices.isna().mean() * 100 > max_missing_pct]
    if len(bad):
        print(f"Dropping tickers with >{max_missing_pct}% missing: {list(bad)}")
        prices = prices.drop(columns=bad)
    prices = prices.ffill(limit=ffill_limit)                       
    return prices.dropna(how="any")

def run_pipeline() -> None:
    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    universe = config.TICKERS + [config.BENCHMARK]
    print(f"Downloading {len(universe)} symbols from {config.DATA_START} ...")
    raw = download_prices(universe, config.DATA_START)
    raw.to_csv(config.RAW_DIR / "prices_raw.csv")

    report = validate_prices(raw)
    report.to_csv(config.PROCESSED_DIR / "data_quality_report.csv")
    print("\n--- Data quality report (worst 8 by missing %) ---")
    print(report.head(8).to_string())

    missing = set(universe) - set(raw.dropna(axis=1, how="all").columns)
    if missing:
        print(f"\nWARNING: failed to download: {sorted(missing)}")

    clean = clean_prices(raw)
    stocks = clean.drop(columns=[config.BENCHMARK])
    benchmark = clean[[config.BENCHMARK]]
    stocks.to_csv(config.PROCESSED_DIR / "prices_stocks.csv")
    benchmark.to_csv(config.PROCESSED_DIR / "prices_benchmark.csv")

    print(f"\nClean dataset: {stocks.shape[0]} days x {stocks.shape[1]} stocks")
    print(f"Date range: {stocks.index.min().date()} to {stocks.index.max().date()}")

if __name__ == "__main__":
    run_pipeline()