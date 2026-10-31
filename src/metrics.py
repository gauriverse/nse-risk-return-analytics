import numpy as np
import pandas as pd
from scipy import stats

from src import config

def log_returns(prices: pd.DataFrame) -> pd.DataFrame: # daily log returns
    return np.log(prices / prices.shift(1)).dropna()

def distribution_summary(returns: pd.DataFrame) -> pd.DataFrame:
    def jb(s: pd.Series) -> pd.Series: # annulaized return/vol plus shape statistics 
        res = stats.jarque_bera(s)
        return pd.Series({"jb_stat": res.statistic, "jb_pvalue": res.pvalue})

    summary = pd.DataFrame({
        "ann_log_return": returns.mean() * config.TRADING_DAYS,
        "ann_volatility": returns.std() * np.sqrt(config.TRADING_DAYS),
        "skewness": returns.skew(),
        "excess_kurtosis": returns.kurt(),   
        "worst_day": returns.min(),
        "best_day": returns.max(),
    })
    summary = summary.join(returns.apply(jb).T)
    summary["reject_normality"] = summary["jb_pvalue"] < 0.05
    return summary

def drawdown_series(returns: pd.DataFrame) -> pd.DataFrame: # drawdown from running peak
    wealth = np.exp(returns.cumsum())
    return wealth / wealth.cummax() - 1

def risk_metrics(returns: pd.DataFrame, rf: float = config.RISK_FREE_RATE,
                 alpha: float = 0.05) -> pd.DataFrame:
    # Return, volatility, Sharpe, Sortino, max drawdown, historical VaR/CVaR
    td = config.TRADING_DAYS
    rf_log = np.log(1 + rf)                       
    ann_ret_log = returns.mean() * td
    vol = returns.std() * np.sqrt(td)

    rf_daily = rf_log / td
    downside = np.sqrt((np.minimum(returns - rf_daily, 0) ** 2).mean()) * np.sqrt(td)

    q = returns.quantile(alpha)                   
    tail = returns.where(returns <= q)           
    out = pd.DataFrame({
        "cagr": np.exp(ann_ret_log) - 1,
        "ann_volatility": vol,
        "sharpe": (ann_ret_log - rf_log) / vol,
        "sortino": (ann_ret_log - rf_log) / downside,
        "max_drawdown": drawdown_series(returns).min(),
        "var_95": -q,
        "cvar_95": -tail.mean(),
    })
    return out