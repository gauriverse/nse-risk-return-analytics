"""Portfolio optimization: min-variance, max-Sharpe, efficient frontier, steepest descent."""
import numpy as np
import pandas as pd
from scipy.optimize import minimize

from src import config

RF_LOG = np.log(1 + config.RISK_FREE_RATE)


def annual_inputs(returns: pd.DataFrame):
    # Annualized mean return vector and covariance matrix
    return returns.mean() * config.TRADING_DAYS, returns.cov() * config.TRADING_DAYS


def _solve(objective, n, cap, extra_constraints=()):
    # Minimize objective with: weights sum to 1, each weight between 0 and cap
    constraints = [{"type": "eq", "fun": lambda w: w.sum() - 1}, *extra_constraints]
    res = minimize(objective, np.full(n, 1 / n), method="SLSQP",
                   bounds=[(0, cap)] * n, constraints=constraints,
                   options={"maxiter": 500, "ftol": 1e-10})
    if not res.success:
        raise RuntimeError(res.message)
    return res.x


def min_variance(cov, cap=0.15):
    return _solve(lambda w: w @ cov @ w, len(cov), cap)


def max_sharpe(mu, cov, cap=0.15):
    return _solve(lambda w: -(w @ mu - RF_LOG) / np.sqrt(w @ cov @ w), len(mu), cap)


def efficient_frontier(mu, cov, cap=0.15, n_points=40):
    # Lowest risk for each target return, from the min-variance point upward
    n = len(mu)
    r_lo = min_variance(cov, cap) @ mu

    r_hi, left = 0.0, 1.0                       
    for m in np.sort(mu)[::-1]:
        take = min(cap, left)
        r_hi += take * m
        left -= take
        if left <= 1e-12:
            break

    rows = []
    for r in np.linspace(r_lo, r_hi - 1e-4, n_points):
        con = {"type": "eq", "fun": lambda w, r=r: w @ mu - r}
        try:
            w = _solve(lambda w: w @ cov @ w, n, cap, [con])
            rows.append({"target_return": r, "volatility": np.sqrt(w @ cov @ w)})
        except RuntimeError:
            continue                           
    return pd.DataFrame(rows)

def _project_to_simplex(v):
    # Closest point to v with all weights >= 0 and sum = 1
    u = np.sort(v)[::-1]
    css = np.cumsum(u) - 1
    k = np.arange(1, len(v) + 1)
    rho = np.nonzero(u - css / k > 0)[0][-1]
    return np.maximum(v - css[rho] / (rho + 1), 0)


def steepest_descent_min_var(cov, steps=5000):
    # Steepest descent for minimum variance: step downhill, then project back
    # onto valid weights (non-negative, summing to 1)
    n = len(cov)
    w = np.full(n, 1 / n)
    lr = 1 / (2 * np.linalg.eigvalsh(cov).max())   # safe step size
    history = []
    for _ in range(steps):
        w = _project_to_simplex(w - lr * 2 * cov @ w)
        history.append(w @ cov @ w)
    return w, history