#!/usr/bin/env python3
"""Computes agreement statistics for the CZT reliability kit and writes reliability_report.md.

Usage: python scripts/analyze_reliability.py <manuscript_source_folder>
Reads (whichever exist):
  1_second_coder/second_coder_workbook.xlsx           (second coder, blind)
  2_scenario_raters/scenario_rater_A.xlsx, _B.xlsx     (independent raters, blind)
  3_screening/screening_S1.xlsx, screening_S2.xlsx     (two screeners)
Only pandas, numpy and openpyxl are required.
"""
import sys, pathlib
import numpy as np
import pandas as pd

KIT = pathlib.Path(__file__).resolve().parents[1]
SRC = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else KIT.parent
out = []

def kappa(a, b, categories=None, weights=None):
    """Cohen's kappa; weights None (nominal), 'linear' or 'quadratic' (ordinal categories in order)."""
    a = list(a); b = list(b)
    cats = categories or sorted(set(a) | set(b))
    k = len(cats); idx = {c: i for i, c in enumerate(cats)}
    O = np.zeros((k, k))
    for x, y in zip(a, b): O[idx[x], idx[y]] += 1
    n = O.sum()
    if n == 0: return float('nan')
    E = np.outer(O.sum(1), O.sum(0)) / n
    if weights is None: W = 1 - np.eye(k)
    else:
        d = np.abs(np.subtract.outer(np.arange(k), np.arange(k))) / max(k - 1, 1)
        W = d if weights == 'linear' else d ** 2
    den = (W * E).sum()
    return 1.0 if den == 0 else 1 - (W * O).sum() / den

def interp(k):
    if np.isnan(k): return 'n/a'
    return 'poor' if k < 0.2 else 'fair' if k < 0.4 else 'moderate' if k < 0.6 else 'substantial' if k < 0.8 else 'almost perfect'

def read_sheet(path, sheet, header_row):
    return pd.read_excel(path, sheet_name=sheet, header=header_row)

# ------------------------------------------------ 1. literature coding
p = KIT / '1_second_coder' / 'second_coder_workbook.xlsx'
dims = ['provenance', 'context', 'authority', 'channel', 'friction', 'challenge', 'feedback']
if p.exists():
    sec = read_sheet(p, 'Coding', 1).dropna(subset=['key'])
    sec = sec[sec[dims].notna().all(axis=1)]
    if len(sec):
        first = pd.read_csv(SRC / 'data' / 'literature_coding_matrix.csv').set_index('key')
        out.append(f'## 1. Literature classification: second coder (n = {len(sec)} sources)\n')
        out.append('| Dimension | Exact agreement | Weighted kappa (linear) | Interpretation |\n|---|---:|---:|---|')
        ks, exact_all = [], []
        for d in dims:
            a = first.loc[sec.key, d].astype(int).tolist(); b = sec[d].astype(int).tolist()
            ex = np.mean(np.array(a) == np.array(b)); kv = kappa(a, b, [0, 1, 2], 'linear')
            ks.append(kv); exact_all += list(np.array(a) == np.array(b))
            out.append(f'| {d} | {ex:.0%} | {kv:.2f} | {interp(kv)} |')
        out.append(f'| **All codes** | {np.mean(exact_all):.0%} | mean {np.nanmean(ks):.2f} | |\n')
        dis = [(k, d, int(first.loc[k, d]), int(v)) for k, row in sec.set_index('key').iterrows() for d, v in row[dims].items() if int(first.loc[k, d]) != int(v)]
        out.append(f'Disagreements to resolve by discussion ({len(dis)}): ' + '; '.join(f'{k}/{d}: {x}→{y}' for k, d, x, y in dis) + '\n')
        out.append(f'Suggested manuscript text: "A second author, blind to the first coder\'s codes, independently classified a stratified random sample of {len(sec)} of the 66 sources ({len(sec)/66:.0%}). Exact agreement on the seven dimensions was {np.mean(exact_all):.0%}, and linearly weighted Cohen\'s kappa ranged from {np.nanmin(ks):.2f} to {np.nanmax(ks):.2f} (mean {np.nanmean(ks):.2f}). The {len(dis)} disagreements were resolved by discussion [describe], and the codebook was [unchanged / clarified for …]."\n')

# ------------------------------------------------ 2. scenario raters
VARS = ['provenance', 'context', 'authority', 'channel_integrity', 'consequence', 'urgency', 'secrecy', 'novelty', 'irreversibility']
rater = {}
for r in 'AB':
    p = KIT / '2_scenario_raters' / f'scenario_rater_{r}.xlsx'
    if p.exists():
        df = read_sheet(p, 'Rating', 1).dropna(subset=['scenario_id'])
        df = df[df[VARS].notna().all(axis=1)]
        if len(df): rater[r] = df.set_index('scenario_id')[VARS].astype(float)
if rater:
    sc = pd.read_csv(SRC / 'data' / 'scenario_vignettes.csv').set_index('scenario_id')
    par = pd.read_csv(SRC / 'data' / 'decision_parameters.csv').set_index('symbol')['value'].to_dict()
    W = np.array([par['w_p'], par['w_c'], par['w_a'], par['w_h']]); V = np.array([par['v_q'], par['v_u'], par['v_s'], par['v_n'], par['v_i']])
    def decisions(scores):
        s = sc.loc[scores.index].copy(); s[VARS] = scores[VARS]
        A = np.round(s[VARS[:4]].values @ W, 9); R = np.round(s[VARS[4:]].values @ V, 9)
        f = s['flags'].fillna('')
        M = (f.str.contains('cred') | (f.str.contains('priv') & ((s.provenance < .5) | (s.authority < .5))) |
             (f.str.contains('payee') & (s.authority < .5) & ((s.urgency >= .5) | (s.secrecy >= .5))) |
             (f.str.contains('data') & (s.channel_integrity < .5))).values
        return pd.Series(np.select([M, (A >= par['tau_A']) & (R < par['tau_R']), (A < par['tau_A_low']) | (R >= par['tau_R_high'])], [3, 0, 2], 1), index=s.index)
    auth = sc[VARS]
    D0 = decisions(auth)
    out.append('## 2. Independent scenario ratings\n')
    if len(rater) == 2:
        common = rater['A'].index.intersection(rater['B'].index)
        out.append(f'Rater A vs Rater B on {len(common)} vignettes (quadratic weighted kappa per variable):\n')
        out.append('| Variable | kappa A–B | kappa A–authors | kappa B–authors |\n|---|---:|---:|---:|')
        for v in VARS:
            cats = sorted(set(auth[v]) | set(rater['A'][v]) | set(rater['B'][v]))
            kab = kappa(rater['A'].loc[common, v], rater['B'].loc[common, v], cats, 'quadratic')
            ka = kappa(rater['A'].loc[common, v], auth.loc[common, v], cats, 'quadratic')
            kb = kappa(rater['B'].loc[common, v], auth.loc[common, v], cats, 'quadratic')
            out.append(f'| {v} | {kab:.2f} | {ka:.2f} | {kb:.2f} |')
        mean_scores = (rater['A'].loc[common] + rater['B'].loc[common]) / 2
        rater['mean(A,B)'] = mean_scores
    names = {0: 'Routine', 1: 'Step-up/callback', 2: 'Dual approval/hold', 3: 'Reject/block'}
    out.append('\n| Score source | Decisions identical to author-scored | Weighted kappa (decision level) | Deceptive routed Routine | Legitimate escalated |\n|---|---:|---:|---:|---:|')
    gt = sc['ground_truth']
    for name, sco in rater.items():
        D = decisions(sco); idx = D.index
        same = (D == D0.loc[idx]).mean(); kd = kappa(D, D0.loc[idx], [0, 1, 2, 3], 'linear')
        miss = int(((D == 0) & (gt.loc[idx] == 'deceptive')).sum()); fesc = int(((D != 0) & (gt.loc[idx] == 'legitimate')).sum())
        out.append(f'| Rater {name} | {same:.0%} | {kd:.2f} | {miss} | {fesc} |')
    out.append(f'| Authors (reported) | 100% | 1.00 | {int(((D0 == 0) & (gt == "deceptive")).sum())} | {int(((D0 != 0) & (gt == "legitimate")).sum())} |\n')
    out.append('Suggested manuscript text: "Two raters who did not write the vignettes independently scored all 60 vignettes with the rubric, blind to the authors\' scores and to the ground-truth labels. Agreement between the raters was [range of kappa] (quadratic weighted kappa per variable). Recomputing the decisions from each rater\'s scores reproduced the author-scored decision in [x]% and [y]% of vignettes; with rater scores, [m] deceptive requests were processed as routine and [f] legitimate requests were escalated, compared with 0 and 6 for the author scores."\n')

# ------------------------------------------------ 3. screening
s1p, s2p = KIT / '3_screening' / 'screening_S1.xlsx', KIT / '3_screening' / 'screening_S2.xlsx'
if s1p.exists() and s2p.exists():
    s1 = pd.read_excel(s1p, 'Screening').set_index('record_id'); s2 = pd.read_excel(s2p, 'Screening').set_index('record_id')
    done = s1.abstract_decision.notna() & s2.abstract_decision.notna()
    ka = kappa(s1.loc[done, 'abstract_decision'], s2.loc[done, 'abstract_decision'])
    out.append(f'## 3. Screening of the {int(done.sum())} records not excludable from titles\n')
    out.append(f'Abstract-level agreement between screeners: {np.mean(s1.loc[done,"abstract_decision"]==s2.loc[done,"abstract_decision"]):.0%}, Cohen\'s kappa {ka:.2f} ({interp(ka)}).\n')
    fin = s1['final_decision'].fillna('')
    ab_ex = int((s1.abstract_decision == 'EXCLUDE').sum()) if fin.eq('').all() else None
    counts = s1['final_code'].value_counts().to_dict()
    out.append(f'Final decisions (from screening_S1.xlsx final columns): {fin.value_counts().to_dict()}; exclusion codes: {counts}\n')
    out.append('Update Table 5 of the manuscript with these counts (records screened at abstract, excluded with reasons, full texts assessed, included).\n')

if not out:
    out.append('No completed workbooks found. Fill in the workbooks first (see README).')
(KIT / 'reliability_report.md').write_text('# CZT reliability report\n\n' + '\n'.join(out) + '\n', encoding='utf-8')
print('\n'.join(out))
