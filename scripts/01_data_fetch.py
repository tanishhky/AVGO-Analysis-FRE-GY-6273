"""
================================================================================
01_data_fetch.py
Pulls AVGO + comparable peer market data via yfinance.
Output -> <project_root>/data/

Washington Square Research Partners | NYU MSFE Equity Research
Tanishk Yadav | Martin Baretto | Ramana Sriram
================================================================================
"""
import yfinance as yf
import pandas as pd
import numpy as np
import os
import json
import warnings

# --- Portable path resolution (relative to script location) ---
from pathlib import Path
SCRIPT_DIR   = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
warnings.filterwarnings('ignore')

DATA_DIR = str(PROJECT_ROOT / 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Per user preference: always use 'Close' (NEVER 'Adj Close')
PRICE_COL = 'Close'

PEER_TICKERS = {
    'AVGO': 'Broadcom',
    'NVDA': 'Nvidia',
    'AMD':  'Advanced Micro Devices',
    'MRVL': 'Marvell Technology',
    'QCOM': 'Qualcomm',
    'TXN':  'Texas Instruments',
    'TSM':  'Taiwan Semiconductor',
    'INTC': 'Intel',
}

INDICES = {'^GSPC': 'S&P 500', '^SOX': 'PHLX Semiconductor', '^TNX': '10Y UST'}


def fetch_prices():
    print("=" * 60)
    print("Fetching 5-year price history")
    print("=" * 60)
    all_tickers = list(PEER_TICKERS.keys()) + list(INDICES.keys())
    df = yf.download(all_tickers, period='5y', interval='1d',
                     auto_adjust=False, progress=False)[PRICE_COL]
    df.to_csv(f'{DATA_DIR}/prices_5y.csv')
    print(f"Shape: {df.shape}, latest: {df.index[-1].date()}")
    print(df.tail(2).round(2).to_string())
    return df


def fetch_avgo_fundamentals():
    print("\n" + "=" * 60)
    print("Fetching AVGO fundamentals")
    print("=" * 60)
    t = yf.Ticker('AVGO')

    info = t.info
    safe_info = {}
    for k, v in info.items():
        try:
            json.dumps(v)
            safe_info[k] = v
        except Exception:
            safe_info[k] = str(v)
    with open(f'{DATA_DIR}/avgo_info.json', 'w') as f:
        json.dump(safe_info, f, indent=2, default=str)

    fin = t.financials
    bal = t.balance_sheet
    cf = t.cashflow

    fin.to_csv(f'{DATA_DIR}/avgo_income_stmt.csv')
    bal.to_csv(f'{DATA_DIR}/avgo_balance_sheet.csv')
    cf.to_csv(f'{DATA_DIR}/avgo_cashflow.csv')

    print(f"Years available: {[c.year for c in fin.columns]}")
    if 'Total Revenue' in fin.index:
        rev_latest = fin.loc['Total Revenue'].iloc[0] / 1e9
        print(f"Latest annual revenue: ${rev_latest:.2f}B")
    cur_price = info.get('currentPrice') or info.get('regularMarketPrice')
    mcap = (info.get('marketCap') or 0) / 1e9
    print(f"Current price: ${cur_price}, Mkt cap: ${mcap:.1f}B")
    return info, fin, bal, cf


def fetch_peers():
    print("\n" + "=" * 60)
    print("Peer fundamental snapshot")
    print("=" * 60)
    rows = []
    for tkr, name in PEER_TICKERS.items():
        try:
            info = yf.Ticker(tkr).info
            rows.append({
                'Ticker': tkr,
                'Name': name,
                'Price': info.get('currentPrice') or info.get('regularMarketPrice'),
                'MarketCap_B': (info.get('marketCap') or 0) / 1e9,
                'EV_B': (info.get('enterpriseValue') or 0) / 1e9,
                'TrailingPE': info.get('trailingPE'),
                'ForwardPE': info.get('forwardPE'),
                'EV_to_Revenue': info.get('enterpriseToRevenue'),
                'EV_to_EBITDA': info.get('enterpriseToEbitda'),
                'GrossMargin': info.get('grossMargins'),
                'OpMargin': info.get('operatingMargins'),
                'NetMargin': info.get('profitMargins'),
                'RevenueGrowth': info.get('revenueGrowth'),
                'EarningsGrowth': info.get('earningsGrowth'),
                'Beta': info.get('beta'),
                'DividendYield': info.get('dividendYield'),
                'Revenue_TTM_B': (info.get('totalRevenue') or 0) / 1e9,
                'EBITDA_TTM_B': (info.get('ebitda') or 0) / 1e9,
                'Debt_B': (info.get('totalDebt') or 0) / 1e9,
                'Cash_B': (info.get('totalCash') or 0) / 1e9,
            })
        except Exception as e:
            print(f"  {tkr} failed: {e}")
    df = pd.DataFrame(rows)
    df.to_csv(f'{DATA_DIR}/peer_metrics.csv', index=False)
    print(df[['Ticker', 'Price', 'MarketCap_B', 'ForwardPE',
              'EV_to_EBITDA', 'GrossMargin', 'OpMargin']].round(2).to_string(index=False))
    return df


def fetch_treasury():
    print("\n" + "=" * 60)
    print("Risk-free rate (10Y UST via ^TNX)")
    print("=" * 60)
    tnx = yf.download('^TNX', period='1mo', auto_adjust=False, progress=False)[PRICE_COL]
    if isinstance(tnx, pd.DataFrame):
        tnx = tnx.iloc[:, 0]
    rate = float(tnx.iloc[-1]) / 100  # ^TNX quoted as % * 10
    print(f"10Y UST: {rate * 100:.3f}% as of {tnx.index[-1].date()}")
    with open(f'{DATA_DIR}/risk_free.json', 'w') as f:
        json.dump({'rate_10y_pct': rate * 100, 'date': str(tnx.index[-1].date())}, f, indent=2)
    return rate


def compute_returns_and_beta(prices):
    print("\n" + "=" * 60)
    print("Beta & return statistics (vs S&P 500)")
    print("=" * 60)
    rets = prices.pct_change().dropna()
    mkt = rets['^GSPC']
    out = []
    for tkr in PEER_TICKERS:
        if tkr in rets.columns:
            r = rets[tkr]
            beta = np.cov(r, mkt)[0, 1] / np.var(mkt)
            ann_ret = (1 + r.mean()) ** 252 - 1
            ann_vol = r.std() * np.sqrt(252)
            sharpe = ann_ret / ann_vol if ann_vol > 0 else np.nan
            out.append({
                'Ticker': tkr,
                'Beta': round(beta, 3),
                'AnnRet_5Y': round(ann_ret * 100, 2),
                'AnnVol_5Y': round(ann_vol * 100, 2),
                'Sharpe': round(sharpe, 3),
            })
    df = pd.DataFrame(out)
    df.to_csv(f'{DATA_DIR}/beta_returns.csv', index=False)
    print(df.to_string(index=False))
    return df


if __name__ == '__main__':
    prices = fetch_prices()
    info, fin, bal, cf = fetch_avgo_fundamentals()
    peers = fetch_peers()
    rf = fetch_treasury()
    betas = compute_returns_and_beta(prices)
    print("\n" + "=" * 60)
    print(f"Data fetch complete. Files written to {DATA_DIR}")
    print("=" * 60)
