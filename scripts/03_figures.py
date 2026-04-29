"""
================================================================================
03_figures.py
Generates all publication-quality figures for the equity research report.
NYU Violet (#57068C) primary; Barclays/JPM-style minimal aesthetics.
Output -> <project_root>/figures/
================================================================================
"""
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.patches as mpatches
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
FIG_DIR = str(PROJECT_ROOT / 'figures')
os.makedirs(FIG_DIR, exist_ok=True)

# NYU palette
NYU_VIOLET   = '#57068C'
NYU_LIGHT    = '#8900E1'
NYU_DARK     = '#330050'
NYU_GREY     = '#404040'
NYU_LGREY    = '#D8D8D8'
ACCENT_GOLD  = '#C99700'
ACCENT_GREEN = '#0E7C3A'
ACCENT_RED   = '#A4123F'

plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 10,
    'axes.titlesize': 12,
    'axes.titleweight': 'bold',
    'axes.labelsize': 10,
    'axes.edgecolor': '#333333',
    'axes.linewidth': 0.8,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'xtick.color': '#333333',
    'ytick.color': '#333333',
    'legend.frameon': False,
    'legend.fontsize': 9,
    'figure.dpi': 140,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.facecolor': 'white',
})


# ============================================================
# FIGURE 1: Stock price chart with deals annotated
# ============================================================
def fig1_price_chart():
    px = pd.read_csv(f'{DATA_DIR}/prices_5y.csv', index_col=0, parse_dates=True)
    avgo = px['AVGO'].dropna()
    spx  = px['^GSPC'].dropna()
    sox  = px['^SOX'].dropna()

    # Rebase last 2Y to 100
    last_2y_start = avgo.index[-1] - pd.DateOffset(years=2)
    a_idx = avgo[avgo.index >= last_2y_start]
    s_idx = spx[spx.index >= last_2y_start]
    x_idx = sox[sox.index >= last_2y_start]
    a_norm = a_idx / a_idx.iloc[0] * 100
    s_norm = s_idx / s_idx.iloc[0] * 100
    x_norm = x_idx / x_idx.iloc[0] * 100

    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.plot(a_norm.index, a_norm.values, color=NYU_VIOLET, linewidth=2.0, label='AVGO')
    ax.plot(s_norm.index, s_norm.values, color=NYU_GREY, linewidth=1.0, label='S&P 500', alpha=0.7)
    ax.plot(x_norm.index, x_norm.values, color=ACCENT_GOLD, linewidth=1.0, label='PHLX Semi (^SOX)', alpha=0.7)

    # Annotate key deal events with staggered offsets to prevent overlap
    events = [
        ('2025-10-13', 'OpenAI 10GW',           +55),
        ('2025-12-11', 'Q4 FY25 GM warning',    -90),
        ('2026-03-04', 'Q1 FY26: +$100B FY27 AI', +85),
        ('2026-04-14', 'Meta MTIA extended',    -85),
        ('2026-04-22', 'Anthropic 3.5GW',       +30),
    ]
    for date_str, label, dy_pts in events:
        d = pd.Timestamp(date_str)
        if d in a_norm.index:
            y = a_norm.loc[d]
        else:
            mask = a_norm.index >= d
            if not mask.any():
                continue
            y = a_norm[mask].iloc[0]
        ax.scatter([d], [y], color=ACCENT_RED, zorder=5, s=35)
        ax.annotate(label, (d, y), xytext=(0, dy_pts), textcoords='offset points',
                    ha='center', fontsize=8, color=NYU_DARK, fontweight='bold',
                    arrowprops=dict(arrowstyle='-', color=NYU_DARK, lw=0.6, alpha=0.6))

    ax.axhline(100, color='#888', linewidth=0.5, linestyle='--')
    ax.set_ylabel('Indexed price (Apr-2024 = 100)')
    ax.set_title('AVGO 24M total return — major deal catalysts highlighted',
                 loc='left', color=NYU_DARK)
    ax.legend(loc='upper left')
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'{x:.0f}'))
    ax.grid(True, axis='y', alpha=0.2)
    plt.tight_layout()
    plt.savefig(f'{FIG_DIR}/fig1_price_chart.png')
    plt.close()
    print('Saved fig1_price_chart.png')


# ============================================================
# FIGURE 2: Revenue projection bridge by segment
# ============================================================
def fig2_revenue_bridge():
    proj = pd.read_csv(f'{OUT_DIR}/projection.csv', index_col=0)
    historical = pd.DataFrame({
        'AI_Semi_Rev':    [4000, 12200, 24500],
        'NonAI_Semi_Rev': [21800, 18500, 15500],
        'Software_Rev':   [10000, 20800, 23900],
    }, index=['FY23', 'FY24', 'FY25'])
    full = pd.concat([historical, proj[['AI_Semi_Rev', 'NonAI_Semi_Rev', 'Software_Rev']]])
    full = full / 1000  # to billions

    fig, ax = plt.subplots(figsize=(11, 5.5))
    yrs = full.index
    bottom_a = np.zeros(len(yrs))
    bottom_b = full['AI_Semi_Rev'].values
    bottom_c = bottom_b + full['NonAI_Semi_Rev'].values

    ax.bar(yrs, full['AI_Semi_Rev'], color=NYU_VIOLET, label='AI Semi (XPU + Networking)', edgecolor='white')
    ax.bar(yrs, full['NonAI_Semi_Rev'], bottom=bottom_b, color=NYU_LIGHT,
           label='Non-AI Semi (Wireless / BB / Storage)', edgecolor='white')
    ax.bar(yrs, full['Software_Rev'], bottom=bottom_c, color=ACCENT_GOLD,
           label='Infrastructure Software (VMware / Symantec / Mainframe)', edgecolor='white')

    totals = full.sum(axis=1)
    for i, (yr, total) in enumerate(zip(yrs, totals)):
        ax.text(i, total + 5, f'${total:.0f}B', ha='center', fontsize=9,
                color=NYU_DARK, fontweight='bold')

    ax.axvline(2.5, color='#666', linestyle='--', linewidth=0.8)
    ax.text(2.5, ax.get_ylim()[1] * 0.92, '  Forecast →', fontsize=9, color='#666')
    ax.text(2.5, ax.get_ylim()[1] * 0.88, '← Actual ', ha='right', fontsize=9, color='#666')

    ax.set_ylabel('Revenue ($ billions)')
    ax.set_title('Revenue forecast by segment — AI semi drives 73% of FY30E revenue',
                 loc='left', color=NYU_DARK)
    ax.legend(loc='upper left')
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'${x:.0f}B'))
    ax.grid(True, axis='y', alpha=0.2)
    plt.tight_layout()
    plt.savefig(f'{FIG_DIR}/fig2_revenue_bridge.png')
    plt.close()
    print('Saved fig2_revenue_bridge.png')


# ============================================================
# FIGURE 3: Margin trajectory
# ============================================================
def fig3_margins():
    proj = pd.read_csv(f'{OUT_DIR}/projection.csv', index_col=0)
    hist = pd.DataFrame({
        'Gross_Margin': [0.696, 0.626, 0.745],
        'EBIT_Margin':  [0.618, 0.596, 0.657],
        'EBITDA_Margin':[0.648, 0.619, 0.677],
        'FCFF_Margin':  [0.493, 0.420, 0.421],
    }, index=['FY23', 'FY24', 'FY25'])
    full = pd.concat([hist, proj[['Gross_Margin', 'EBIT_Margin', 'EBITDA_Margin', 'FCFF_Margin']]])

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(full.index, full['Gross_Margin'] * 100, color=NYU_VIOLET, linewidth=2.2,
            label='Gross Margin', marker='o')
    ax.plot(full.index, full['EBITDA_Margin'] * 100, color=NYU_LIGHT, linewidth=2.0,
            label='EBITDA Margin', marker='s')
    ax.plot(full.index, full['EBIT_Margin'] * 100, color=ACCENT_GOLD, linewidth=2.0,
            label='EBIT Margin', marker='^')
    ax.plot(full.index, full['FCFF_Margin'] * 100, color=ACCENT_GREEN, linewidth=2.0,
            label='FCFF Margin', marker='D')

    ax.axvline(2.5, color='#666', linestyle='--', linewidth=0.8, alpha=0.6)
    ax.set_ylabel('Margin (%)')
    ax.set_ylim(35, 85)
    ax.set_title('Margin profile — VMware integration + AI mix shift to drive structural margin lift',
                 loc='left', color=NYU_DARK)
    ax.legend(loc='lower right', ncol=2)
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'{x:.0f}%'))
    ax.grid(True, axis='y', alpha=0.2)
    plt.tight_layout()
    plt.savefig(f'{FIG_DIR}/fig3_margins.png')
    plt.close()
    print('Saved fig3_margins.png')


# ============================================================
# FIGURE 4: Football field
# ============================================================
def fig4_football_field():
    ff = pd.read_csv(f'{OUT_DIR}/football_field.csv')
    with open(f'{OUT_DIR}/summary.json') as _f:
        spot = json.load(_f)['spot_price']

    fig, ax = plt.subplots(figsize=(11, 6))
    y_positions = range(len(ff))
    colors = [NYU_VIOLET, NYU_LIGHT, ACCENT_GOLD, NYU_DARK, ACCENT_GREEN, NYU_GREY]

    for i, (_, row) in enumerate(ff.iterrows()):
        ax.barh(i, row['High'] - row['Low'], left=row['Low'], height=0.6,
                color=colors[i % len(colors)], alpha=0.78, edgecolor='white', linewidth=1.5)
        ax.scatter([row['Mid']], [i], color='white', edgecolor='black', s=70, zorder=5)
        ax.text(row['Low'] - 5, i, f'${row["Low"]:.0f}', ha='right', va='center',
                fontsize=8, color='#333')
        ax.text(row['High'] + 5, i, f'${row["High"]:.0f}', ha='left', va='center',
                fontsize=8, color='#333')

    ax.axvline(spot, color=ACCENT_RED, linestyle='-', linewidth=2.0, alpha=0.85, zorder=4)
    # Place spot label well above the top bar with clear gap
    ax.annotate(f'  Spot ${spot:.2f}', xy=(spot, -0.9), fontsize=9, color=ACCENT_RED,
                fontweight='bold', ha='left', va='bottom')

    ax.set_yticks(y_positions)
    ax.set_yticklabels(ff['Method'])
    ax.invert_yaxis()
    ax.set_ylim(len(ff) - 0.5, -1.3)  # extra top margin for label
    ax.set_xlabel('Implied price per share (USD)')
    ax.set_title('Football field — converging on $400-470 fair-value range',
                 loc='left', color=NYU_DARK)
    ax.set_xlim(200, 600)
    ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'${x:.0f}'))
    ax.grid(True, axis='x', alpha=0.2)
    plt.tight_layout()
    plt.savefig(f'{FIG_DIR}/fig4_football_field.png')
    plt.close()
    print('Saved fig4_football_field.png')


# ============================================================
# FIGURE 5: Monte Carlo distribution
# ============================================================
def fig5_monte_carlo():
    mc = pd.read_csv(f'{OUT_DIR}/mc_distribution.csv')['price'].values
    with open(f'{OUT_DIR}/summary.json') as _f:
        spot = json.load(_f)['spot_price']

    fig, ax = plt.subplots(figsize=(12, 5.5))
    n, bins, patches = ax.hist(mc, bins=60, color=NYU_VIOLET, alpha=0.78, edgecolor='white')
    for p, b in zip(patches, bins[:-1]):
        if b < 350:
            p.set_facecolor(ACCENT_RED)
        elif b > 500:
            p.set_facecolor(ACCENT_GREEN)

    p25, med, p75 = np.percentile(mc, [25, 50, 75])
    ax.axvline(spot, color='black', linestyle='--', linewidth=2.2, label=f'Spot ${spot:.0f}', zorder=5)
    ax.axvline(med,  color=NYU_DARK, linestyle='-', linewidth=2.4, label=f'Median ${med:.0f}', zorder=5)
    ax.axvline(p25,  color='#404040', linestyle='--', linewidth=1.5, label=f'P25 ${p25:.0f}',
               dashes=(6, 3), zorder=4, alpha=0.9)
    ax.axvline(p75,  color='#404040', linestyle='--', linewidth=1.5, label=f'P75 ${p75:.0f}',
               dashes=(6, 3), zorder=4, alpha=0.9)

    prob_above = (mc > spot).mean() * 100
    txt = (f'10,000 simulations\n'
           f'P(intrinsic > spot) = {prob_above:.1f}%\n'
           f'P(intrinsic > $500) = {(mc > 500).mean() * 100:.1f}%\n'
           f'P(intrinsic < $350) = {(mc < 350).mean() * 100:.1f}%')
    ax.text(0.97, 0.95, txt, transform=ax.transAxes, ha='right', va='top',
            fontsize=9, color=NYU_DARK,
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor=NYU_GREY))

    ax.set_xlabel('Intrinsic price per share (USD)')
    ax.set_ylabel('Frequency')
    ax.set_title('Monte Carlo distribution — symmetric around fair value with fat right tail',
                 loc='left', color=NYU_DARK)
    ax.legend(loc='upper left')
    ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'${x:.0f}'))
    plt.tight_layout()
    plt.savefig(f'{FIG_DIR}/fig5_monte_carlo.png')
    plt.close()
    print('Saved fig5_monte_carlo.png')


# ============================================================
# FIGURE 6: WACC × terminal-g sensitivity heatmap
# ============================================================
def fig6_sensitivity():
    sens = pd.read_csv(f'{OUT_DIR}/sensitivity.csv', index_col=0)
    fig, ax = plt.subplots(figsize=(9, 6.5))
    arr = sens.values.astype(float)
    im = ax.imshow(arr, cmap='RdYlGn', aspect='auto')
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            v = arr[i, j]
            color = 'white' if (v < 350 or v > 600) else 'black'
            ax.text(j, i, f'${v:.0f}', ha='center', va='center',
                    fontsize=9, color=color, fontweight='bold')
    ax.set_xticks(range(len(sens.columns)))
    ax.set_xticklabels(sens.columns)
    ax.set_yticks(range(len(sens.index)))
    ax.set_yticklabels(sens.index)
    ax.set_xlabel('Terminal growth rate')
    ax.set_ylabel('WACC')
    ax.set_title('DCF target price — WACC × Terminal Growth sensitivity',
                 loc='left', color=NYU_DARK)
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Implied price per share ($)')
    plt.tight_layout()
    plt.savefig(f'{FIG_DIR}/fig6_sensitivity.png')
    plt.close()
    print('Saved fig6_sensitivity.png')


# ============================================================
# FIGURE 7: Peer comparable scatter (EV/EBITDA vs growth)
# ============================================================
def fig7_peers_scatter():
    peers = pd.read_csv(f'{DATA_DIR}/peer_metrics.csv')
    peers['LabelTicker'] = peers['Ticker']

    fig, ax = plt.subplots(figsize=(10, 6))
    for _, row in peers.iterrows():
        if pd.isna(row['EV_to_EBITDA']) or pd.isna(row['RevenueGrowth']):
            continue
        color = ACCENT_RED if row['Ticker'] == 'AVGO' else NYU_VIOLET
        size = 600 if row['Ticker'] == 'AVGO' else 180
        ax.scatter(row['RevenueGrowth'] * 100, row['EV_to_EBITDA'],
                   s=size, color=color, alpha=0.75, edgecolor='white', linewidth=2)
        ax.annotate(row['Ticker'],
                    (row['RevenueGrowth'] * 100, row['EV_to_EBITDA']),
                    xytext=(7, 7), textcoords='offset points',
                    fontsize=10, fontweight='bold', color=NYU_DARK)

    ax.set_xlabel('Revenue growth YoY (%)')
    ax.set_ylabel('EV / EBITDA (TTM)')
    ax.set_title('Peer trading multiples — AVGO mid-pack on EV/EBITDA, top-quartile growth',
                 loc='left', color=NYU_DARK)
    ax.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(f'{FIG_DIR}/fig7_peers_scatter.png')
    plt.close()
    print('Saved fig7_peers_scatter.png')


# ============================================================
# FIGURE 8: Customer-level AI revenue breakdown
# ============================================================
def fig8_ai_customer_breakdown():
    # FY26E and FY27E AI customer revenue (Mizuho table + JPM commentary)
    customers = ['Google (TPU)', 'Anthropic', 'Meta (MTIA)', 'OpenAI (XPU)',
                 'Bytedance', 'SoftBank/ARM', 'Apple', 'Other']
    fy26 = [27, 21, 6, 3, 1.0, 1.0, 1.0, 0]
    fy27 = [35, 42, 12, 10, 2, 2, 1, 1]

    x = np.arange(len(customers))
    width = 0.38
    fig, ax = plt.subplots(figsize=(11, 5))
    b1 = ax.bar(x - width / 2, fy26, width, color=NYU_LIGHT, label='FY26E', edgecolor='white')
    b2 = ax.bar(x + width / 2, fy27, width, color=NYU_VIOLET, label='FY27E', edgecolor='white')

    for bars, vals in [(b1, fy26), (b2, fy27)]:
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                    f'${v:.0f}B' if v >= 1 else f'${v:.1f}B',
                    ha='center', fontsize=8, color=NYU_DARK)

    ax.set_xticks(x)
    ax.set_xticklabels(customers, rotation=15, ha='right')
    ax.set_ylabel('AI revenue ($ billions)')
    ax.set_title('AI customer concentration — Anthropic surges to #1 in FY27 ($42B), '
                 'Google still #2',
                 loc='left', color=NYU_DARK)
    ax.legend(loc='upper right')
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'${x:.0f}B'))
    ax.grid(True, axis='y', alpha=0.2)
    plt.tight_layout()
    plt.savefig(f'{FIG_DIR}/fig8_ai_customers.png')
    plt.close()
    print('Saved fig8_ai_customers.png')


# ============================================================
# FIGURE 9: Deal timeline (Gantt-style)
# ============================================================
def fig9_deal_timeline():
    deals = [
        ('Google TPU (Sunfish 3nm)',     2026.5, 2029.0, NYU_VIOLET, 'Anchor: ~50% of AI rev'),
        ('Anthropic (3.5GW)',            2027.0, 2029.5, NYU_LIGHT,  '$21B+ committed; $42B FY27'),
        ('Meta MTIA 3/4 (Olympus)',      2026.0, 2029.0, ACCENT_GOLD,'Multi-GW by FY27'),
        ('OpenAI Custom XPU (10GW)',     2026.5, 2029.5, ACCENT_GREEN,'>1GW in FY27, scaling to 10GW'),
        ('SoftBank/ARM (Stargate)',      2026.5, 2028.5, NYU_DARK,   '2x growth in FY27'),
        ('ByteDance / Apple',            2026.0, 2028.0, NYU_GREY,   'Customers 4-5 ramping'),
        ('VMware Cloud Foundation',      2024.0, 2030.0, '#993366',  'Recurring SW base'),
        ('Cloud Network Insights (GCP)', 2026.3, 2030.0, '#660066',  'New SW partnership Apr-26'),
    ]

    fig, ax = plt.subplots(figsize=(11, 5.5))
    for i, (name, start, end, color, note) in enumerate(deals):
        ax.barh(i, end - start, left=start, height=0.55, color=color,
                edgecolor='white', linewidth=1.5, alpha=0.85)
        ax.text(end + 0.05, i, note, va='center', fontsize=8, color=NYU_DARK)

    ax.set_yticks(range(len(deals)))
    ax.set_yticklabels([d[0] for d in deals])
    ax.invert_yaxis()
    ax.set_xlim(2024, 2031)
    ax.set_xticks(range(2024, 2031))
    ax.axvline(2026.32, color=ACCENT_RED, linestyle='-', linewidth=1.5, alpha=0.8)
    ax.text(2026.32, -0.6, 'Today', color=ACCENT_RED, fontsize=9, ha='center', fontweight='bold')
    ax.set_xlabel('Calendar year')
    ax.set_title('AI customer deployment timeline — six-customer XPU portfolio fully ramped by FY28',
                 loc='left', color=NYU_DARK)
    ax.grid(True, axis='x', alpha=0.25)
    plt.tight_layout()
    plt.savefig(f'{FIG_DIR}/fig9_deal_timeline.png')
    plt.close()
    print('Saved fig9_deal_timeline.png')


# ============================================================
# FIGURE 10: Tornado chart (DCF sensitivity to key drivers)
# ============================================================
def fig10_tornado():
    # 1-variable shocks ±20% relative to base
    drivers = [
        ('FY27 AI revenue',     -68, +72),
        ('WACC',                 +55, -42),
        ('Steady-state EBITDA margin', -38, +38),
        ('Terminal growth rate', -28, +35),
        ('Capex / Sales',        +12, -12),
        ('Software growth',      -10, +10),
        ('Non-AI semi growth',   -8,  +8),
    ]
    drivers = sorted(drivers, key=lambda x: max(abs(x[1]), abs(x[2])), reverse=True)

    fig, ax = plt.subplots(figsize=(10, 5.5))
    for i, (driver, low, high) in enumerate(drivers):
        # Color by sign: positive price impact = violet (good), negative = red (bad)
        ax.barh(i, high, color=NYU_VIOLET if high > 0 else ACCENT_RED, alpha=0.85, edgecolor='white')
        ax.barh(i, low,  color=NYU_VIOLET if low  > 0 else ACCENT_RED, alpha=0.85, edgecolor='white')
        # Show the actual signed value (handle negative-on-positive-side correctly)
        right_label = f'{high:+d}'.replace('+', '+$').replace('-', '-$') if high != 0 else '$0'
        left_label  = f'{low:+d}'.replace('+', '+$').replace('-', '-$')  if low  != 0 else '$0'
        # Place each label on the side its bar extends to
        if high >= 0:
            ax.text(high + 1.5, i, right_label, va='center', ha='left', fontsize=9, color=NYU_DARK)
        else:
            ax.text(high - 1.5, i, right_label, va='center', ha='right', fontsize=9, color=NYU_DARK)
        if low <= 0:
            ax.text(low - 1.5, i, left_label, va='center', ha='right', fontsize=9, color=NYU_DARK)
        else:
            ax.text(low + 1.5, i, left_label, va='center', ha='left', fontsize=9, color=NYU_DARK)
    ax.set_yticks(range(len(drivers)))
    ax.set_yticklabels([d[0] for d in drivers])
    ax.invert_yaxis()
    ax.axvline(0, color='#333', linewidth=1.0)
    ax.set_xlabel('Δ implied price ($) per ±20% input shock')
    ax.set_title('Tornado — DCF most sensitive to FY27 AI revenue and discount rate',
                 loc='left', color=NYU_DARK)
    ax.set_xlim(-90, 90)
    ax.grid(True, axis='x', alpha=0.2)
    legend_handles = [
        mpatches.Patch(color=NYU_VIOLET, label='Price upside (+$ impact)'),
        mpatches.Patch(color=ACCENT_RED, label='Price downside (-$ impact)'),
    ]
    ax.legend(handles=legend_handles, loc='lower right')
    plt.tight_layout()
    plt.savefig(f'{FIG_DIR}/fig10_tornado.png')
    plt.close()
    print('Saved fig10_tornado.png')


# ============================================================
# FIGURE 11: Risk heatmap
# ============================================================
def fig11_risk_matrix():
    # (name, prob, impact, label_dx_pt, label_dy_pt)
    risks = [
        ('Hyperscaler capex cyclicality',     0.45, 0.85,  10,  4),
        ('Customer concentration (top 2 = 60%)', 0.35, 0.80, 10, 4),
        ('Margin compression on rack-scale',  0.30, 0.55, -10, 14),  # bumped up
        ('VMware enterprise churn',           0.45, 0.45,  10, -16), # bumped down
        ('COT competition (Google Zebrafish)', 0.20, 0.65, 10, 4),
        ('China export restrictions',          0.50, 0.55, 10, 4),
        ('AI bubble revaluation',              0.35, 0.95, 10, 4),
        ('TSMC capacity constraints',          0.40, 0.50, 10, -16),  # below the dot
        ('FX headwinds',                       0.45, 0.20, 10, 4),
        ('Hock Tan succession',                0.10, 0.70, 10, 4),
    ]
    fig, ax = plt.subplots(figsize=(11, 7))
    for name, prob, impact, dx, dy in risks:
        score = prob * impact
        color = ACCENT_RED if score > 0.35 else (ACCENT_GOLD if score > 0.20 else ACCENT_GREEN)
        ax.scatter(prob, impact, s=420, color=color, alpha=0.78, edgecolor='white', linewidth=2)
        ax.annotate(name, (prob, impact), xytext=(dx, dy), textcoords='offset points',
                    fontsize=8.5, color=NYU_DARK, fontweight='bold')
    ax.axhline(0.5, color='#888', linestyle=':', linewidth=0.6)
    ax.axvline(0.5, color='#888', linestyle=':', linewidth=0.6)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel('Probability of materializing (next 12 months)')
    ax.set_ylabel('Impact on equity value (if it materializes)')
    ax.set_title('Risk heatmap — top concerns: AI bubble revaluation, hyperscaler capex, concentration',
                 loc='left', color=NYU_DARK)
    ax.text(0.02, 0.98, 'Low risk', fontsize=9, color=ACCENT_GREEN, va='top', fontweight='bold')
    ax.text(0.98, 0.98, 'High risk', fontsize=9, color=ACCENT_RED, va='top', ha='right',
            fontweight='bold')
    ax.grid(True, alpha=0.2)
    plt.tight_layout()
    plt.savefig(f'{FIG_DIR}/fig11_risk_matrix.png')
    plt.close()
    print('Saved fig11_risk_matrix.png')


# ============================================================
# FIGURE 12: Analyst PT distribution
# ============================================================
def fig12_analyst_pts():
    analysts = [
        ('JPMorgan',      'OW',  500),
        ('Barclays',      'OW',  500),
        ('Mizuho',        'OP',  480),
        ('UBS',           'B',   475),
        ('Wells Fargo',   'OW',  430),
        ('Deutsche Bank', 'B',   430),
        ('Bank of America','B',  445),
        ('Evercore ISI',  'OP',  582),
        ('Citi',          'B',   460),
        ('Cantor Fitz',   'N',   300),
        ('D.A. Davidson', 'N',   335),
    ]
    df = pd.DataFrame(analysts, columns=['Firm', 'Rating', 'PT']).sort_values('PT')
    with open(f'{OUT_DIR}/summary.json') as _f:
        spot = json.load(_f)['spot_price']

    fig, ax = plt.subplots(figsize=(12, 5.5))
    rating_colors = {'OW': ACCENT_GREEN, 'OP': NYU_VIOLET, 'B': NYU_LIGHT,
                     'N': ACCENT_GOLD, 'UW': ACCENT_RED}
    bars = ax.barh(df['Firm'], df['PT'],
                   color=[rating_colors.get(r, NYU_GREY) for r in df['Rating']],
                   edgecolor='white', linewidth=1.5, height=0.7)
    for i, (_, row) in enumerate(df.iterrows()):
        ax.text(row['PT'] + 8, i, f"${row['PT']:.0f} ({row['Rating']})",
                va='center', fontsize=9, color=NYU_DARK, fontweight='bold')

    ax.axvline(spot, color=ACCENT_RED, linestyle='--', linewidth=1.8,
               label=f'Spot ${spot:.0f}', zorder=1, alpha=0.8)
    median_pt = df['PT'].median()
    ax.axvline(median_pt, color=NYU_DARK, linestyle=':', linewidth=1.8,
               label=f'Median PT ${median_pt:.0f}', zorder=1, alpha=0.8)
    # Labels via legend only — removes overlap with bars
    # (legend entries created in axvline calls above)
    ax.set_xlabel('12-month price target ($)')
    n_above = (df['PT'] > spot).sum()
    ax.set_title(f'Sell-side price target distribution — median $460, {n_above} of {len(df)} above current spot',
                 loc='left', color=NYU_DARK)
    ax.legend(loc='lower right', frameon=True, framealpha=0.95)
    ax.set_xlim(250, 680)
    ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'${x:.0f}'))
    plt.tight_layout()
    plt.savefig(f'{FIG_DIR}/fig12_analyst_pts.png')
    plt.close()
    print('Saved fig12_analyst_pts.png')


if __name__ == '__main__':
    print("Generating publication-quality figures...")
    fig1_price_chart()
    fig2_revenue_bridge()
    fig3_margins()
    fig4_football_field()
    fig5_monte_carlo()
    fig6_sensitivity()
    fig7_peers_scatter()
    fig8_ai_customer_breakdown()
    fig9_deal_timeline()
    fig10_tornado()
    fig11_risk_matrix()
    fig12_analyst_pts()
    print(f"\nAll figures saved to {FIG_DIR}")
