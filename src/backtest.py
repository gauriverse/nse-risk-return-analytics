import numpy as np
import pandas as pd

from src import config


def portfolio_returns(returns: pd.DataFrame, weights) -> pd.Series:
    # Daily simple-return series of a fixed-weight portfolio rebalanced daily
    simple = np.exp(returns) - 1
    return simple @ np.asarray(weights)


def performance(daily: pd.Series, rf: float = config.RISK_FREE_RATE) -> dict:
    # Headline statistics from a daily simple-return series
    td = config.TRADING_DAYS
    wealth = (1 + daily).cumprod()
    years = len(daily) / td
    cagr = wealth.iloc[-1] ** (1 / years) - 1
    vol = daily.std() * np.sqrt(td)
    return {
        "cagr": cagr,
        "volatility": vol,
        "sharpe": (cagr - rf) / vol,
        "max_drawdown": (wealth / wealth.cummax() - 1).min(),
        "final_value_of_1": wealth.iloc[-1],
    }


def avg_pairwise_corr(returns: pd.DataFrame) -> float:
    c = returns.corr().values
    return c[~np.eye(len(c), dtype=bool)].mean()