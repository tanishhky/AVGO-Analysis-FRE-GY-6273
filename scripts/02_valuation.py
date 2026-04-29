"""
================================================================================
02_valuation.py
Master valuation engine for AVGO:
    1. DCF (FCFF, 5-year explicit + Gordon terminal)
    2. Sum-of-the-Parts (Semiconductor Solutions vs. Infrastructure Software)
    3. Trading Comparables (peer-derived target ranges)
    4. Monte Carlo simulation around DCF (10,000 paths)
    5. Football-field synthesis of valuation ranges

Washington Square Research Partners | NYU MSFE Equity Research
Tanishk Yadav | Martin Baretto | Ramana Sriram
================================================================================
"""
import numpy as np
import pandas as pd
import json
import os
import warnings

# --- Portable path resolution (relative to script location) ---
from pathlib import Path
SCRIPT_DIR   = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
warnings.filterwarnings('ignore')

DATA_DIR = str(PROJECT_ROOT / 'data')
OUT_DIR = str(PROJECT_ROOT / 'output')
os.makedirs(OUT_DIR, exist_ok=True)

np.random.seed(42)

# =========================================================================
# 1. ASSUMPTIONS
#    Sources: AVGO Q1 FY26 8-K (Mar 4, 2026); JPM/UBS/Mizuho/Wells/DB/Barclays
#    research notes; AVGO 10-K FY25; Bloomberg tearsheet 3/12/2026
# =========================================================================
ASSUMPTIONS = {
    'fiscal_year_end': 'Oct',
    'report_date': '2026-04-25',
    'spot_price': 422.76,
    'shares_diluted_mn': 4969.0,
    'net_debt_25_mn': 48958.0,
    # FY25A actuals (10-K)
    'rev_25': 63887.0,
    'ebitda_25': 43204.0,
    'ebit_25': 41997.0,
    'fcf_25': 26914.0,
    'tax_rate': 0.18,
    # WACC inputs
    # Note: 5Y daily beta of 1.633 reflects elevated AI volatility in 2024-25;
    # for valuation we use Bloomberg's 2Y weekly beta of ~1.20, consistent with
    # JPM/UBS/Mizuho practice. Sensitivity table covers the range.
    'rf': 0.0431,            # 10Y UST 24-Apr-26
    'erp': 0.050,            # Damodaran 2025 implied ERP for US large-caps
    'beta_levered': 1.20,    # Bloomberg 2Y weekly beta (analyst convention)
    'beta_5y_daily': 1.633,  # Reported separately in report
    'pretax_kd': 0.050,      # AVGO senior notes ~4.5-5.5% blended
    'target_debt_weight': 0.15,
    # Long-run terminal
    'terminal_growth': 0.030,
}

# AI revenue ramp assumptions (consensus: JPM $120B / Mizuho $101B / UBS $130B / WF $107B / DB $107B / Barclays $150B)
# We use a midpoint consistent with management's "$100B+" line for FY27 and embed bull/bear in MC.
AI_REV_PATH = {        # all $mn
    'FY26': 60000,     # Mgmt: ~$65B for FY26 (Q1 8.4 + Q2 10.7 implied annualized)
    'FY27': 115000,    # Midpoint of analyst range
    'FY28': 165000,    # 43% YoY (deceleration)
    'FY29': 205000,    # 24% YoY
    'FY30': 235000,    # 15% YoY
}

NONAI_SEMI_REV_PATH = {  # legacy semis (wireless, broadband, storage, networking ex-AI)
    'FY26': 16500,
    'FY27': 17000,
    'FY28': 17750,
    'FY29': 18500,
    'FY30': 19250,
}

SOFTWARE_REV_PATH = {    # VMware + Symantec + Mainframe (CA)
    'FY26': 28500,
    'FY27': 31000,
    'FY28': 33500,
    'FY29': 35500,
    'FY30': 37500,
}

# Margin assumptions
GROSS_MARGIN_PATH = {'FY26': 0.770, 'FY27': 0.775, 'FY28': 0.780, 'FY29': 0.780, 'FY30': 0.780}
OPEX_PCT_REV_PATH = {'FY26': 0.085, 'FY27': 0.075, 'FY28': 0.072, 'FY29': 0.070, 'FY30': 0.069}
DA_PCT_REV_PATH   = {'FY26': 0.012, 'FY27': 0.010, 'FY28': 0.009, 'FY29': 0.009, 'FY30': 0.008}
CAPEX_PCT_REV     = {'FY26': 0.012, 'FY27': 0.010, 'FY28': 0.010, 'FY29': 0.010, 'FY30': 0.010}
WC_CHG_PCT_REV    = {'FY26': 0.010, 'FY27': 0.012, 'FY28': 0.010, 'FY29': 0.008, 'FY30': 0.008}


# =========================================================================
# 2. PROJECTED P&L AND FCFF
# =========================================================================
def build_projection():
    years = ['FY26', 'FY27', 'FY28', 'FY29', 'FY30']
    df = pd.DataFrame(index=years)
    df['AI_Semi_Rev']     = [AI_REV_PATH[y] for y in years]
    df['NonAI_Semi_Rev']  = [NONAI_SEMI_REV_PATH[y] for y in years]
    df['Software_Rev']    = [SOFTWARE_REV_PATH[y] for y in years]
    df['Total_Revenue']   = df[['AI_Semi_Rev', 'NonAI_Semi_Rev', 'Software_Rev']].sum(axis=1)
    df['Rev_Growth_YoY']  = [
        (df.loc[y, 'Total_Revenue'] / ASSUMPTIONS['rev_25'] - 1) if i == 0
        else (df.loc[y, 'Total_Revenue'] / df.loc[years[i - 1], 'Total_Revenue'] - 1)
        for i, y in enumerate(years)
    ]
    df['Gross_Margin']    = [GROSS_MARGIN_PATH[y] for y in years]
    df['Gross_Profit']    = df['Total_Revenue'] * df['Gross_Margin']
    df['Opex']            = df['Total_Revenue'] * pd.Series(OPEX_PCT_REV_PATH).reindex(years).values
    df['EBIT']            = df['Gross_Profit'] - df['Opex']
    df['EBIT_Margin']     = df['EBIT'] / df['Total_Revenue']
    df['DA']              = df['Total_Revenue'] * pd.Series(DA_PCT_REV_PATH).reindex(years).values
    df['EBITDA']          = df['EBIT'] + df['DA']
    df['EBITDA_Margin']   = df['EBITDA'] / df['Total_Revenue']
    df['Tax']             = df['EBIT'] * ASSUMPTIONS['tax_rate']
    df['NOPAT']           = df['EBIT'] - df['Tax']
    df['Capex']           = df['Total_Revenue'] * pd.Series(CAPEX_PCT_REV).reindex(years).values
    df['WC_Change']       = df['Total_Revenue'] * pd.Series(WC_CHG_PCT_REV).reindex(years).values
    df['FCFF']            = df['NOPAT'] + df['DA'] - df['Capex'] - df['WC_Change']
    df['FCFF_Margin']     = df['FCFF'] / df['Total_Revenue']
    # Round dollar columns to 0dp; keep ratio columns at 4dp
    dollar_cols = ['AI_Semi_Rev', 'NonAI_Semi_Rev', 'Software_Rev', 'Total_Revenue',
                   'Gross_Profit', 'Opex', 'EBIT', 'DA', 'EBITDA', 'Tax', 'NOPAT',
                   'Capex', 'WC_Change', 'FCFF']
    df[dollar_cols] = df[dollar_cols].round(0)
    ratio_cols = ['Rev_Growth_YoY', 'Gross_Margin', 'EBIT_Margin', 'EBITDA_Margin', 'FCFF_Margin']
    df[ratio_cols] = df[ratio_cols].round(4)
    return df


# =========================================================================
# 3. WACC
# =========================================================================
def compute_wacc():
    a = ASSUMPTIONS
    ke = a['rf'] + a['beta_levered'] * a['erp']
    kd_at = a['pretax_kd'] * (1 - a['tax_rate'])
    we = 1 - a['target_debt_weight']
    wacc = we * ke + a['target_debt_weight'] * kd_at
    return {
        'cost_of_equity': ke,
        'after_tax_cost_of_debt': kd_at,
        'weight_equity': we,
        'weight_debt': a['target_debt_weight'],
        'wacc': wacc,
    }


# =========================================================================
# 4. DCF
# =========================================================================
def run_dcf(proj=None, wacc=None, terminal_g=None):
    if proj is None:
        proj = build_projection()
    if wacc is None:
        wacc = compute_wacc()['wacc']
    if terminal_g is None:
        terminal_g = ASSUMPTIONS['terminal_growth']

    fcff = proj['FCFF'].values
    n = len(fcff)
    discount_factors = np.array([(1 + wacc) ** (i + 0.5) for i in range(n)])  # mid-year convention
    pv_fcff = fcff / discount_factors
    terminal_value = fcff[-1] * (1 + terminal_g) / (wacc - terminal_g)
    pv_tv = terminal_value / ((1 + wacc) ** (n - 0.5))
    enterprise_value = pv_fcff.sum() + pv_tv
    equity_value = enterprise_value - ASSUMPTIONS['net_debt_25_mn']
    target_price = equity_value / ASSUMPTIONS['shares_diluted_mn']
    return {
        'fcff': fcff,
        'pv_fcff': pv_fcff,
        'terminal_value': terminal_value,
        'pv_terminal': pv_tv,
        'enterprise_value': enterprise_value,
        'equity_value': equity_value,
        'target_price': target_price,
        'wacc_used': wacc,
        'terminal_g_used': terminal_g,
        'tv_pct_of_ev': pv_tv / enterprise_value,
    }


def wacc_terminal_sensitivity():
    waccs = np.arange(0.075, 0.121, 0.005)
    gs = np.arange(0.020, 0.041, 0.005)
    proj = build_projection()
    grid = pd.DataFrame(index=[f"{w * 100:.1f}%" for w in waccs],
                        columns=[f"{g * 100:.1f}%" for g in gs], dtype=float)
    for w in waccs:
        for g in gs:
            r = run_dcf(proj, wacc=w, terminal_g=g)
            grid.loc[f"{w * 100:.1f}%", f"{g * 100:.1f}%"] = round(r['target_price'], 1)
    return grid


# =========================================================================
# 5. COMPS
# =========================================================================
def comps_valuation():
    peers = pd.read_csv(f'{DATA_DIR}/peer_metrics.csv')
    avgo_row = peers[peers['Ticker'] == 'AVGO'].iloc[0]
    others = peers[peers['Ticker'].isin(['NVDA', 'AMD', 'MRVL', 'QCOM', 'TXN', 'TSM'])]
    fwd_pe_median = others['ForwardPE'].median()
    fwd_pe_mean   = others['ForwardPE'].mean()
    ev_ebitda_median = others['EV_to_EBITDA'].median()

    # Project CY27 EPS (consensus: JPM $20.45 / Wells $20.24 / UBS $22.76 / Mizuho $18.30 / Barclays $18.60)
    cy27_eps_consensus = 20.00
    proj = build_projection()
    cy27_revenue = proj.loc['FY27', 'Total_Revenue']
    cy27_ebitda = proj.loc['FY27', 'EBITDA']

    # PE-implied target
    pe_low = 18.0
    pe_mid = 22.0
    pe_high = 26.0
    pe_target_low  = pe_low * cy27_eps_consensus
    pe_target_mid  = pe_mid * cy27_eps_consensus
    pe_target_high = pe_high * cy27_eps_consensus

    # EV/EBITDA-implied target (use AVGO target multiple range)
    evx_low, evx_mid, evx_high = 14.0, 18.0, 22.0
    ev_low  = evx_low * cy27_ebitda
    ev_mid  = evx_mid * cy27_ebitda
    ev_high = evx_high * cy27_ebitda
    eq_low  = ev_low - ASSUMPTIONS['net_debt_25_mn']
    eq_mid  = ev_mid - ASSUMPTIONS['net_debt_25_mn']
    eq_high = ev_high - ASSUMPTIONS['net_debt_25_mn']
    px_evx_low  = eq_low / ASSUMPTIONS['shares_diluted_mn']
    px_evx_mid  = eq_mid / ASSUMPTIONS['shares_diluted_mn']
    px_evx_high = eq_high / ASSUMPTIONS['shares_diluted_mn']

    return {
        'peers_table': others,
        'avgo_row': avgo_row,
        'peer_median_fwdpe': fwd_pe_median,
        'peer_mean_fwdpe': fwd_pe_mean,
        'peer_median_evebitda': ev_ebitda_median,
        'cy27_eps_used': cy27_eps_consensus,
        'pe_target_low': pe_target_low,
        'pe_target_mid': pe_target_mid,
        'pe_target_high': pe_target_high,
        'evx_target_low': px_evx_low,
        'evx_target_mid': px_evx_mid,
        'evx_target_high': px_evx_high,
    }


# =========================================================================
# 6. SOTP
# =========================================================================
def sotp_valuation():
    """
    Two-segment SOTP using FY27E figures.
        - Semiconductor Solutions (AI XPU + Networking + non-AI)
        - Infrastructure Software (VMware + Symantec + Mainframe)
    """
    proj = build_projection()
    fy27 = proj.loc['FY27']

    semi_rev = fy27['AI_Semi_Rev'] + fy27['NonAI_Semi_Rev']
    sw_rev   = fy27['Software_Rev']

    # Approximate segment-level EBITDA margins
    semi_ebitda_margin = 0.62   # AI mix dilutes vs SW; consistent with mgmt commentary
    sw_ebitda_margin   = 0.77   # software is higher-margin
    semi_ebitda = semi_rev * semi_ebitda_margin
    sw_ebitda   = sw_rev * sw_ebitda_margin

    # Segment multiples — anchored to segment-pure peers
    # Semi: blend NVDA / MRVL / TXN ~18-22x EV/EBITDA fwd
    # SW: blend ORCL / MSFT enterprise software ~16-20x EV/EBITDA
    semi_mult_low, semi_mult_mid, semi_mult_high = 16.0, 20.0, 24.0
    sw_mult_low, sw_mult_mid, sw_mult_high       = 14.0, 17.0, 20.0

    sotp = pd.DataFrame({
        'Segment':           ['Semiconductor Solutions', 'Infrastructure Software'],
        'FY27E_Revenue':     [semi_rev, sw_rev],
        'EBITDA_Margin':     [semi_ebitda_margin, sw_ebitda_margin],
        'FY27E_EBITDA':      [semi_ebitda, sw_ebitda],
        'EV_EBITDA_Mult_Low':  [semi_mult_low, sw_mult_low],
        'EV_EBITDA_Mult_Mid':  [semi_mult_mid, sw_mult_mid],
        'EV_EBITDA_Mult_High': [semi_mult_high, sw_mult_high],
    })
    sotp['EV_Low']  = sotp['FY27E_EBITDA'] * sotp['EV_EBITDA_Mult_Low']
    sotp['EV_Mid']  = sotp['FY27E_EBITDA'] * sotp['EV_EBITDA_Mult_Mid']
    sotp['EV_High'] = sotp['FY27E_EBITDA'] * sotp['EV_EBITDA_Mult_High']

    total_ev_low  = sotp['EV_Low'].sum()
    total_ev_mid  = sotp['EV_Mid'].sum()
    total_ev_high = sotp['EV_High'].sum()
    eq_low  = total_ev_low  - ASSUMPTIONS['net_debt_25_mn']
    eq_mid  = total_ev_mid  - ASSUMPTIONS['net_debt_25_mn']
    eq_high = total_ev_high - ASSUMPTIONS['net_debt_25_mn']
    px_low  = eq_low  / ASSUMPTIONS['shares_diluted_mn']
    px_mid  = eq_mid  / ASSUMPTIONS['shares_diluted_mn']
    px_high = eq_high / ASSUMPTIONS['shares_diluted_mn']

    return {
        'sotp_table': sotp,
        'total_ev_low': total_ev_low,
        'total_ev_mid': total_ev_mid,
        'total_ev_high': total_ev_high,
        'price_low': px_low,
        'price_mid': px_mid,
        'price_high': px_high,
    }


# =========================================================================
# 7. MONTE CARLO
# =========================================================================
def monte_carlo(n_sims=10000):
    """
    Stochastic drivers (independent draws):
      - FY27 AI revenue ($B)            : Normal(115, 25)   [mgmt guide $100B+, analyst range 100-150]
      - AI growth FY27->FY30 CAGR       : Normal(0.30, 0.10)
      - Long-run terminal growth        : Normal(0.030, 0.005)
      - WACC                            : Normal(base, 0.005)
      - Steady-state EBITDA margin      : Normal(0.685, 0.025)
      - Capex/Sales                     : Normal(0.011, 0.003)
      - Non-AI semi growth              : Normal(0.04, 0.02)
      - Software growth                 : Normal(0.07, 0.025)
    """
    rng = np.random.default_rng(seed=42)
    base_wacc = compute_wacc()['wacc']

    fy27_ai_b      = rng.normal(125.0, 25.0, n_sims)        # $B - Street mean
    ai_post27_cagr = rng.normal(0.30, 0.10, n_sims)
    term_gs        = rng.normal(0.030, 0.005, n_sims)
    waccs          = rng.normal(base_wacc, 0.005, n_sims)
    ebitda_mgs     = rng.normal(0.685, 0.025, n_sims)
    capex_pct      = rng.normal(0.011, 0.003, n_sims)
    nonai_growth   = rng.normal(0.040, 0.020, n_sims)
    sw_growth      = rng.normal(0.070, 0.025, n_sims)

    # Starting points anchored in FY25A reality
    nonai_rev_fy25 = 16000.0
    sw_rev_fy25    = 23400.0

    # Project AI from FY26 -> FY30 implied by FY27 anchor
    # FY26 = ~52% of FY27 (mgmt: $60B vs $115B mid)
    prices = []
    for i in range(n_sims):
        if waccs[i] <= term_gs[i] + 0.005:
            continue
        if fy27_ai_b[i] < 50:    # implausibly low; reject
            continue

        ai_fy27_mn = fy27_ai_b[i] * 1000.0
        ai_fy26_mn = ai_fy27_mn * 0.52
        ai_path_mn = [ai_fy26_mn,
                      ai_fy27_mn,
                      ai_fy27_mn * (1 + ai_post27_cagr[i]),
                      ai_fy27_mn * (1 + ai_post27_cagr[i]) ** 2,
                      ai_fy27_mn * (1 + ai_post27_cagr[i]) ** 3]

        nonai_path = [nonai_rev_fy25 * (1 + nonai_growth[i]) ** (y + 1) for y in range(5)]
        sw_path    = [sw_rev_fy25    * (1 + sw_growth[i])    ** (y + 1) for y in range(5)]

        rev_path    = np.array(ai_path_mn) + np.array(nonai_path) + np.array(sw_path)
        ebitda_path = rev_path * ebitda_mgs[i]
        nopat_path  = ebitda_path * 0.985 * (1 - ASSUMPTIONS['tax_rate'])
        capex_path  = rev_path * capex_pct[i]
        wc_path     = rev_path * 0.009
        fcff_path   = nopat_path - capex_path - wc_path

        df_factors = np.array([(1 + waccs[i]) ** (y + 0.5) for y in range(5)])
        pv_fcff = fcff_path / df_factors
        tv = fcff_path[-1] * (1 + term_gs[i]) / (waccs[i] - term_gs[i])
        pv_tv = tv / ((1 + waccs[i]) ** (5 - 0.5))
        ev = pv_fcff.sum() + pv_tv
        eq = ev - ASSUMPTIONS['net_debt_25_mn']
        prices.append(eq / ASSUMPTIONS['shares_diluted_mn'])

    arr = np.array(prices)
    return {
        'distribution': arr,
        'mean': float(np.mean(arr)),
        'median': float(np.median(arr)),
        'std': float(np.std(arr)),
        'p5': float(np.percentile(arr, 5)),
        'p25': float(np.percentile(arr, 25)),
        'p75': float(np.percentile(arr, 75)),
        'p95': float(np.percentile(arr, 95)),
        'prob_above_spot': float((arr > ASSUMPTIONS['spot_price']).mean()),
        'prob_above_500':  float((arr > 500).mean()),
        'prob_below_350':  float((arr < 350).mean()),
    }


# =========================================================================
# 8. SYNTHESIS
# =========================================================================
def synthesize(dcf, comps, sotp, mc, sens):
    # DCF range: pull from sensitivity table at +/- 100bps WACC at base terminal g of 3%
    base_wacc = dcf['wacc_used']
    # Lookup nearest WACC rows
    wacc_keys = [float(s.strip('%')) / 100 for s in sens.index]
    target_g_col = '3.0%'
    base_idx = int(np.argmin(np.abs(np.array(wacc_keys) - base_wacc)))
    high_wacc_idx = max(0, base_idx - 1)   # lower WACC -> higher price
    low_wacc_idx  = min(len(wacc_keys) - 1, base_idx + 1)
    dcf_low_px  = float(sens.iloc[low_wacc_idx][target_g_col])
    dcf_mid_px  = float(sens.iloc[base_idx][target_g_col])
    dcf_high_px = float(sens.iloc[high_wacc_idx][target_g_col])

    rows = [
        ('DCF (5Y FCFF + Gordon TV)',     dcf_low_px,           dcf_mid_px,           dcf_high_px),
        ('SOTP (FY27E EV/EBITDA)',         sotp['price_low'],   sotp['price_mid'],    sotp['price_high']),
        ('Trading Comps (Fwd P/E)',        comps['pe_target_low'], comps['pe_target_mid'], comps['pe_target_high']),
        ('Trading Comps (EV/EBITDA)',      comps['evx_target_low'], comps['evx_target_mid'], comps['evx_target_high']),
        ('Monte Carlo (P25/Median/P75)',   mc['p25'],           mc['median'],         mc['p75']),
        ('Street Consensus (last 30D)',    430.0,               469.0,                500.0),
    ]
    return pd.DataFrame(rows, columns=['Method', 'Low', 'Mid', 'High'])


if __name__ == '__main__':
    print("\n" + "#" * 70)
    print("AVGO VALUATION ENGINE")
    print("Washington Square Research Partners | NYU MSFE Equity Research")
    print("#" * 70)

    proj = build_projection()
    print("\n" + "=" * 60)
    print("PROJECTED P&L AND FCFF (FY26E - FY30E)  [$ in mn]")
    print("=" * 60)
    print(proj.T.to_string())
    proj.to_csv(f'{OUT_DIR}/projection.csv')

    wacc_info = compute_wacc()
    print("\n" + "=" * 60)
    print("WACC")
    print("=" * 60)
    for k, v in wacc_info.items():
        print(f"  {k:30s} {v * 100:7.3f}%")

    dcf = run_dcf()
    print("\n" + "=" * 60)
    print("DCF VALUATION")
    print("=" * 60)
    print(f"  Enterprise Value      ${dcf['enterprise_value']:>15,.0f} mn")
    print(f"  Less Net Debt         ${ASSUMPTIONS['net_debt_25_mn']:>15,.0f} mn")
    print(f"  Equity Value          ${dcf['equity_value']:>15,.0f} mn")
    print(f"  Diluted Shares (mn)    {ASSUMPTIONS['shares_diluted_mn']:>15,.0f}")
    print(f"  Implied Price/Share   ${dcf['target_price']:>15,.2f}")
    print(f"  Spot Price            ${ASSUMPTIONS['spot_price']:>15,.2f}")
    print(f"  Implied Upside         {(dcf['target_price'] / ASSUMPTIONS['spot_price'] - 1) * 100:>15,.1f}%")
    print(f"  TV % of EV             {dcf['tv_pct_of_ev'] * 100:>15,.1f}%")

    sens = wacc_terminal_sensitivity()
    print("\n" + "=" * 60)
    print("DCF SENSITIVITY (Rows = WACC, Cols = Terminal g)")
    print("=" * 60)
    print(sens.to_string())
    sens.to_csv(f'{OUT_DIR}/sensitivity.csv')

    comps = comps_valuation()
    print("\n" + "=" * 60)
    print("TRADING COMPARABLES")
    print("=" * 60)
    print(f"  Peer Median Forward P/E    : {comps['peer_median_fwdpe']:.2f}x")
    print(f"  Peer Median EV/EBITDA      : {comps['peer_median_evebitda']:.2f}x")
    print(f"  Forward P/E target range   : ${comps['pe_target_low']:.0f} / ${comps['pe_target_mid']:.0f} / ${comps['pe_target_high']:.0f}")
    print(f"  EV/EBITDA target range     : ${comps['evx_target_low']:.0f} / ${comps['evx_target_mid']:.0f} / ${comps['evx_target_high']:.0f}")

    sotp = sotp_valuation()
    print("\n" + "=" * 60)
    print("SUM-OF-THE-PARTS")
    print("=" * 60)
    print(sotp['sotp_table'].to_string(index=False))
    print(f"\n  SOTP Implied Price Range : ${sotp['price_low']:.0f} / ${sotp['price_mid']:.0f} / ${sotp['price_high']:.0f}")
    sotp['sotp_table'].to_csv(f'{OUT_DIR}/sotp.csv', index=False)

    mc = monte_carlo(n_sims=10000)
    print("\n" + "=" * 60)
    print("MONTE CARLO (10,000 paths)")
    print("=" * 60)
    print(f"  Mean intrinsic price       : ${mc['mean']:.2f}")
    print(f"  Median                     : ${mc['median']:.2f}")
    print(f"  Std deviation              : ${mc['std']:.2f}")
    print(f"  5th percentile             : ${mc['p5']:.2f}")
    print(f"  25th percentile            : ${mc['p25']:.2f}")
    print(f"  75th percentile            : ${mc['p75']:.2f}")
    print(f"  95th percentile            : ${mc['p95']:.2f}")
    print(f"  Prob (intrinsic > spot)    : {mc['prob_above_spot'] * 100:.1f}%")
    print(f"  Prob (intrinsic > $500)    : {mc['prob_above_500'] * 100:.1f}%")
    print(f"  Prob (intrinsic < $350)    : {mc['prob_below_350'] * 100:.1f}%")
    pd.DataFrame({'price': mc['distribution']}).to_csv(f'{OUT_DIR}/mc_distribution.csv', index=False)

    football = synthesize(dcf, comps, sotp, mc, sens)
    football.to_csv(f'{OUT_DIR}/football_field.csv', index=False)
    print("\n" + "=" * 60)
    print("FOOTBALL FIELD (target price by method)")
    print("=" * 60)
    print(football.to_string(index=False))

    summary = {
        'spot_price': ASSUMPTIONS['spot_price'],
        'wacc': wacc_info['wacc'],
        'dcf_target': dcf['target_price'],
        'dcf_upside': dcf['target_price'] / ASSUMPTIONS['spot_price'] - 1,
        'sotp_mid': sotp['price_mid'],
        'comps_pe_mid': comps['pe_target_mid'],
        'comps_evx_mid': comps['evx_target_mid'],
        'mc_median': mc['median'],
        'mc_mean': mc['mean'],
        'mc_p25': mc['p25'],
        'mc_p75': mc['p75'],
        'mc_prob_above_spot': mc['prob_above_spot'],
        'football_high': float(football['High'].max()),
        'football_low':  float(football['Low'].min()),
        'football_avg_mid': float(football['Mid'].mean()),
    }
    with open(f'{OUT_DIR}/summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\nResults written to {OUT_DIR}/")
