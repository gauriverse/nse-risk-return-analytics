"""Central configuration for the NSE Risk-Return Analytics project."""
from pathlib import Path

# ---------- Paths ----------
ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
FIG_DIR = ROOT / "outputs" / "figures"
POWERBI_DIR = ROOT / "outputs" / "powerbi"

# ---------- Universe: ticker -> sector ----------
SECTOR_MAP = {
    "HDFCBANK.NS": "Banking & Financials", "ICICIBANK.NS": "Banking & Financials",
    "SBIN.NS": "Banking & Financials", "KOTAKBANK.NS": "Banking & Financials",
    "AXISBANK.NS": "Banking & Financials", "BAJFINANCE.NS": "Banking & Financials",
    "TCS.NS": "IT", "INFY.NS": "IT", "HCLTECH.NS": "IT",
    "RELIANCE.NS": "Energy & Utilities", "ONGC.NS": "Energy & Utilities",
    "NTPC.NS": "Energy & Utilities", "POWERGRID.NS": "Energy & Utilities",
    "HINDUNILVR.NS": "FMCG", "ITC.NS": "FMCG",
    "NESTLEIND.NS": "FMCG", "BRITANNIA.NS": "FMCG",
    "MARUTI.NS": "Auto", "M&M.NS": "Auto", "BAJAJ-AUTO.NS": "Auto",
    "SUNPHARMA.NS": "Pharma", "DRREDDY.NS": "Pharma", "CIPLA.NS": "Pharma",
    "TATASTEEL.NS": "Metals", "HINDALCO.NS": "Metals", "JSWSTEEL.NS": "Metals",
    "LT.NS": "Infra & Materials", "ULTRACEMCO.NS": "Infra & Materials",
    "ASIANPAINT.NS": "Consumer", "TITAN.NS": "Consumer",
}
TICKERS = list(SECTOR_MAP.keys())
BENCHMARK = "^NSEI"  # NIFTY 50

# ---------- Time windows ----------
DATA_START = "2018-01-01"
TRAIN_START, TRAIN_END = "2019-01-01", "2022-12-31"
TEST_START = "2023-01-01"

# ---------- Finance constants ----------
TRADING_DAYS = 252          # trading days per year
RISK_FREE_RATE = 0.065      # ~6.5% annual (approx. Indian 10Y G-Sec yield)