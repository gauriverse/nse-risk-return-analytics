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