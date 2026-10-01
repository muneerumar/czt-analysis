#!/usr/bin/env python3
"""Runs the CZT Monte Carlo simulation study and writes results, figures and quoted numbers.

Usage (from the repository root):  python sim/run_simulation.py [--quick]
Outputs: sim/results/*.csv, sim/results/simulation_numbers.txt, figures/Figure_18_*.pdf, figures/Figure_19_*.pdf
Deterministic: all random streams derive from fixed seeds.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from model import CONFIGS, CLASSES, load_params, replicate  # noqa: E402

ROOT = HERE.parent
QUICK = '--quick' in sys.argv          # smoke test: fewer runs, written to sim/results_quick/ only
RES = HERE / ('results_quick' if QUICK else 'results'); RES.mkdir(exist_ok=True)
FIG = RES if QUICK else ROOT / 'figures'; FIG.mkdir(exist_ok=True)
plt.rcParams.update({'font.size': 8.5, 'axes.titlesize': 9, 'legend.fontsize': 7, 'savefig.bbox': 'tight', 'pdf.fonttype': 42})
RATIOS = [5, 20, 100, 1000]
MAIN = ['ZT baseline', 'Awareness training', 'Uniform callback', 'CZT (full)']
COMPARATORS = ['ZT baseline', 'Awareness training', 'Uniform callback']
numbers = []
note = lambda k, v: numbers.append(f'{k}: {v}')

P = load_params()
REPS = 20 if QUICK else P['replications']

# ------------------------------------------------------------------ main experiment
rows, cls_rows = [], []
for rep in range(REPS):
    out = replicate(P, seed=1000 + rep)
    for cfg, (tot, hc) in out.items():
        n = tot['requests']
        row = dict(rep=rep, config=cfg, harm_per_10k=tot['harm'] / n * 1e4,
                   legit_escalation_pct=tot['legit_escalated'] / tot['legit'] * 100,
                   delay_per_10k=tot['delay'] / n * 1e4, deceptive=tot['deceptive'], harm=tot['harm'])
        for r in RATIOS:
            row[f'cost_per_10k_r{r}'] = (r * tot['harm'] + tot['delay']) / n * 1e4
        rows.append(row)
        for j, c in enumerate(CLASSES[2:], start=2):
            cls_rows.append(dict(rep=rep, config=cfg, adversary=c, harmful=int(hc[j])))
runs = pd.DataFrame(rows); runs.to_csv(RES / 'replications.csv', index=False)


def ci(x):
    x = np.asarray(x, float); m = x.mean(); h = 1.96 * x.std(ddof=1) / np.sqrt(len(x))
    return m, m - h, m + h


summ = []
for cfg in CONFIGS:
    d = runs[runs.config == cfg]
    s = dict(config=cfg)
    for col in ['harm_per_10k', 'legit_escalation_pct', 'delay_per_10k'] + [f'cost_per_10k_r{r}' for r in RATIOS]:
        m, lo, hi = ci(d[col]); s[col] = round(m, 3); s[col + '_lo'] = round(lo, 3); s[col + '_hi'] = round(hi, 3)
    summ.append(s)
summ = pd.DataFrame(summ); summ.to_csv(RES / 'main_results.csv', index=False)
S = summ.set_index('config')

cls_df = pd.DataFrame(cls_rows)
tot_dec = {}
# attacks generated per class (identical across configurations under common random numbers)
base_counts = cls_df[cls_df.config == 'ZT baseline'].groupby('adversary').harmful.sum()
by_class = cls_df.groupby(['config', 'adversary']).harmful.sum().unstack()
by_class.to_csv(RES / 'harm_by_adversary.csv')

note('replications', REPS); note('requests per replication', P['n_periods'] * P['requests_per_period'])
for cfg in CONFIGS:
    note(f'harm/10k [{cfg}]', f"{S.loc[cfg,'harm_per_10k']:.1f} (95% CI {S.loc[cfg,'harm_per_10k_lo']:.1f}-{S.loc[cfg,'harm_per_10k_hi']:.1f})")
    note(f'legit escalated % [{cfg}]', f"{S.loc[cfg,'legit_escalation_pct']:.1f}")
b = S.loc['ZT baseline', 'harm_per_10k']
for cfg in CONFIGS[1:]:
    note(f'harm reduction vs baseline % [{cfg}]', f"{(1 - S.loc[cfg,'harm_per_10k'] / b) * 100:.0f}")
for adv in ['A1', 'A2', 'A3', 'A4', 'A5']:
    note(f'harm reduction vs baseline % [CZT (full)][{adv}]', f"{(1 - by_class.loc['CZT (full)', adv] / max(1, by_class.loc['ZT baseline', adv])) * 100:.0f}")
    note(f'harm reduction vs baseline % [Uniform callback][{adv}]', f"{(1 - by_class.loc['Uniform callback', adv] / max(1, by_class.loc['ZT baseline', adv])) * 100:.0f}")

# paired difference from removing protected human challenge (common random numbers across configurations)
_w = runs.pivot(index='rep', columns='config', values='harm_per_10k')
_d = _w['CZT - human challenge'] - _w['CZT (full)']
_h = 1.96 * _d.std(ddof=1) / np.sqrt(len(_d))
note('paired harm/10k difference [CZT - human challenge minus CZT (full)]', f'{_d.mean():.3f} (95% interval {_d.mean() - _h:.3f}-{_d.mean() + _h:.3f})')

# break-even cost ratio: smallest c_h/c_d at which CZT (full) has lower expected cost than each comparator
def breakeven(cfg_other, cfg='CZT (full)'):
    dh = S.loc[cfg_other, 'harm_per_10k'] - S.loc[cfg, 'harm_per_10k']       # harm avoided by CZT
    dd = S.loc[cfg, 'delay_per_10k'] - S.loc[cfg_other, 'delay_per_10k']     # extra delay caused by CZT
    if dh <= 0: return float('inf')
    return max(0.0, dd / dh)
for other in COMPARATORS + ['CZT - friction']:
    note(f'break-even c_h/c_d [CZT (full) vs {other}]', f'{breakeven(other):.1f}')

# ------------------------------------------------------------------ global sensitivity (Latin hypercube)
spec = json.loads((HERE / 'parameters.json').read_text(encoding='utf-8'))
uncertain = [k for k, v in spec.items() if not k.startswith('_') and v.get('range') and k != 'c_h_over_c_d']
N_LHS = 60 if QUICK else 400
rng = np.random.default_rng(20260930)
lhs = np.zeros((N_LHS, len(uncertain)))
for j in range(len(uncertain)):
    lhs[:, j] = (rng.permutation(N_LHS) + rng.random(N_LHS)) / N_LHS
samples = []
for k in range(N_LHS):
    Q = dict(P); Q['n_periods'] = 10
    for j, name in enumerate(uncertain):
        lo, hi = spec[name]['range']; Q[name] = lo + lhs[k, j] * (hi - lo)
    out = replicate(Q, seed=50_000 + k, configs=MAIN + ['CZT - friction'])
    rec = {name: Q[name] for name in uncertain}
    for cfg, (tot, _) in out.items():
        rec[f'harm|{cfg}'] = tot['harm'] / tot['requests'] * 1e4
        rec[f'delay|{cfg}'] = tot['delay'] / tot['requests'] * 1e4
    samples.append(rec)
lhs_df = pd.DataFrame(samples); lhs_df.to_csv(RES / 'lhs_samples.csv', index=False)

def cost(df, cfg, r): return r * df[f'harm|{cfg}'] + df[f'delay|{cfg}']
win_rows = []
for r in RATIOS:
    best_other = np.minimum.reduce([cost(lhs_df, c, r) for c in COMPARATORS])
    win = (cost(lhs_df, 'CZT (full)', r) < best_other).mean()
    win_rows.append(dict(ratio=r, share_czt_lowest_cost=win))
    note(f'share of parameter space where CZT (full) has the lowest cost at c_h/c_d={r}', f'{win:.2f}')
wins = pd.DataFrame(win_rows); wins.to_csv(RES / 'lhs_win_share.csv', index=False)
harm_red = 1 - lhs_df['harm|CZT (full)'] / lhs_df['harm|ZT baseline']
note('harm reduction vs baseline across parameter space: median [IQR]', f'{harm_red.median()*100:.0f}% [{harm_red.quantile(.25)*100:.0f}-{harm_red.quantile(.75)*100:.0f}%]')
note('share of parameter space where CZT (full) causes less harm than every comparator',
     f"{(lhs_df['harm|CZT (full)'] < np.minimum.reduce([lhs_df[f'harm|{c}'] for c in COMPARATORS])).mean():.2f}")

def prcc(X: pd.DataFrame, y: pd.Series) -> pd.Series:
    R = X.rank().values; ry = y.rank().values; out = {}
    for j, name in enumerate(X.columns):
        others = np.column_stack([np.ones(len(R)), np.delete(R, j, axis=1)])
        rx = R[:, j] - others @ np.linalg.lstsq(others, R[:, j], rcond=None)[0]
        rr = ry - others @ np.linalg.lstsq(others, ry, rcond=None)[0]
        out[name] = float(np.corrcoef(rx, rr)[0, 1])
    return pd.Series(out)
adv100 = np.minimum.reduce([cost(lhs_df, c, 100) for c in COMPARATORS]) - cost(lhs_df, 'CZT (full)', 100)
pr = prcc(lhs_df[uncertain], pd.Series(adv100)).sort_values(key=np.abs, ascending=False)
pr.rename('prcc_cost_advantage_ratio100').to_csv(RES / 'sensitivity_prcc.csv')
for k, v in pr.head(5).items(): note(f'PRCC (cost advantage, c_h/c_d=100) [{k}]', f'{v:+.2f}')

# ------------------------------------------------------------------ figures
col = {'ZT baseline': '#8c8c8c', 'Awareness training': '#b8a04a', 'Uniform callback': '#d9822b', 'CZT (full)': '#1f5a96'}
fig, ax = plt.subplots(2, 2, figsize=(6.6, 5.4))
order = CONFIGS
y = np.arange(len(order))
a = ax[0, 0]
m = S.loc[order, 'harm_per_10k']; err = np.vstack([m - S.loc[order, 'harm_per_10k_lo'], S.loc[order, 'harm_per_10k_hi'] - m])
a.barh(y, m, xerr=err, color=[col.get(c, '#8fb3d9') for c in order]); a.set_yticks(y); a.set_yticklabels(order); a.invert_yaxis()
a.set_xlabel('Deceptive requests executed per 10,000 requests'); a.set_title('(a) Harmful actions (mean, 95% CI)')
a = ax[0, 1]
a.barh(y, S.loc[order, 'legit_escalation_pct'], color=[col.get(c, '#8fb3d9') for c in order]); a.set_yticks(y); a.set_yticklabels([]); a.invert_yaxis()
a.set_xlabel('Legitimate requests escalated (%)'); a.set_title('(b) Friction on legitimate work')
a = ax[1, 0]
rr = np.logspace(np.log10(2), np.log10(2000), 60)
for cfg in MAIN + ['CZT - friction']:
    c = S.loc[cfg, 'harm_per_10k'] * rr + S.loc[cfg, 'delay_per_10k']
    a.plot(rr, c, label='Vetoes only (CZT - friction)' if cfg == 'CZT - friction' else cfg, color=col.get(cfg, '#3a8a3a'),
           ls='--' if cfg == 'CZT - friction' else '-')
a.set_xscale('log'); a.set_yscale('log'); a.set_xlabel(r'Cost ratio $c_h/c_d$')
a.set_ylabel('Simulated cost per 10,000 requests'); a.legend(frameon=False, fontsize=6.5); a.set_title('(c) Simulated cost (Section 6.6)')
a = ax[1, 1]
advs = ['A1', 'A2', 'A3', 'A4', 'A5']; x = np.arange(5); w = 0.26
for k, cfg in enumerate(['ZT baseline', 'Uniform callback', 'CZT (full)']):
    frac = [by_class.loc[cfg, adv] / max(1, by_class.loc['ZT baseline', adv]) * 100 for adv in advs]
    a.bar(x + (k - 1) * w, frac, w, label=cfg, color=col[cfg])
a.set_xticks(x); a.set_xticklabels(advs); a.set_xlabel('Adversary class (Table 6)'); a.set_ylim(0, 150); a.set_yticks([0, 25, 50, 75, 100])
a.set_ylabel('Harm relative to ZT baseline (%)'); a.legend(frameon=False, ncol=1, loc='upper right', fontsize=6.3, handlelength=1.2); a.set_title('(d) Harm by adversary class')
fig.tight_layout(); fig.savefig(FIG / 'Figure_18_Simulation_Results.pdf'); plt.close(fig)

fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.8), gridspec_kw={'width_ratios': [1.25, 1]})
a = ax[0]
lab = {k: k.replace('_', ' ') for k in pr.index}
a.barh(np.arange(len(pr)), pr.values, color=['#1f5a96' if v > 0 else '#b8322e' for v in pr.values])
a.set_yticks(np.arange(len(pr))); a.set_yticklabels([lab[k] for k in pr.index]); a.invert_yaxis(); a.axvline(0, c='k', lw=.6)
a.set_xlabel('PRCC with CZT cost advantage ($c_h/c_d$=100)'); a.set_title('(a) What drives the advantage')
a = ax[1]
a.plot(wins.ratio, wins.share_czt_lowest_cost * 100, marker='o', color='#1f5a96')
a.set_xscale('log'); a.set_ylim(0, 105); a.set_xlabel('Cost ratio $c_h/c_d$'); a.set_ylabel('Parameter sets (%)')
a.set_title(f'(b) CZT has the lowest cost ({N_LHS} LHS samples)')
fig.tight_layout(); fig.savefig(FIG / 'Figure_19_Simulation_Sensitivity.pdf'); plt.close(fig)

(RES / 'simulation_numbers.txt').write_text('\n'.join(numbers) + '\n', encoding='utf-8')
print('\n'.join(numbers))
