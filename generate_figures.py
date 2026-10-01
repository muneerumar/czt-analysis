#!/usr/bin/env python3
"""Regenerates every data-driven figure and derived table in the manuscript.

Usage:  python generate_figures.py            (run from the package root)
Inputs: data/literature_coding_matrix.csv, data/scenario_vignettes.csv,
        data/decision_parameters.csv, data/analytical_assumptions.csv, data/dependency_matrix.csv
Outputs: figures/*.pdf, data/scenario_results.csv, data/sensitivity_summary.csv,
         data/derived_numbers.txt (every number quoted in the text)
Requires: Python >= 3.9, pandas, numpy, matplotlib. Deterministic (fixed random seed).
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

ROOT = Path(__file__).resolve().parent
DATA, FIG = ROOT / 'data', ROOT / 'figures'
FIG.mkdir(exist_ok=True)
plt.rcParams.update({'font.size': 8.5, 'axes.titlesize': 9, 'axes.labelsize': 8.5, 'legend.fontsize': 7.5,
                     'xtick.labelsize': 7.5, 'ytick.labelsize': 7.5, 'savefig.bbox': 'tight', 'pdf.fonttype': 42})
BLUE, ORANGE, GREEN, RED, GREY = '#1f5a96', '#d9822b', '#3a8a3a', '#b8322e', '#8c8c8c'
out_numbers = []

def note(key, value):
    out_numbers.append(f'{key}: {value}')

def save(fig, name):
    fig.savefig(FIG / name)
    plt.close(fig)

# ---------------------------------------------------------------- literature corpus
lit = pd.read_csv(DATA / 'literature_coding_matrix.csv')
DIMS = ['provenance', 'context', 'authority', 'channel', 'friction', 'challenge', 'feedback']
DIM_LABEL = {'provenance': 'Provenance', 'context': 'Context', 'authority': 'Authority', 'channel': 'Channel',
             'friction': 'Friction', 'challenge': 'Human\nchallenge', 'feedback': 'Feedback'}
note('corpus_size', len(lit))
for k, v in lit.source_type.value_counts().items():
    note(f'type[{k}]', v)
for k, v in lit.research_stream.value_counts().items():
    note(f'stream[{k}]', v)
for d in DIMS:
    note(f'mean[{d}]', round(lit[d].mean(), 2))
    note(f'central2[{d}]', int((lit[d] == 2).sum()))
note('distinct_coverage_profiles', lit[DIMS].drop_duplicates().shape[0])

# Fig 2: annual distribution
counts = lit.groupby('year').size()
fig, ax = plt.subplots(figsize=(6.3, 2.6))
ax.bar(counts.index.astype(str), counts.values, color=BLUE)
ax.set_ylabel('Sources'); ax.set_xlabel('Publication year')
ax.tick_params(axis='x', rotation=60)
ax.set_title(f'Annual distribution of coded sources (N={len(lit)})')
save(fig, 'Figure_02_Annual_Publications.pdf')

# Fig 4: coverage of CZT dimensions (a) distribution of codes, (b) mean by stream
fig, axes = plt.subplots(2, 1, figsize=(6.4, 5.4), gridspec_kw={'height_ratios': [1, 1.05]})
ax = axes[0]
shares = pd.DataFrame({c: lit[DIMS].apply(lambda s: (s == c).mean()) for c in (0, 1, 2)})
order = shares[2].add(shares[1] * 0.5).sort_values(ascending=False).index
left = np.zeros(len(order))
for c, col, lab in ((2, BLUE, 'Central (2)'), (1, '#8fb3d9', 'Substantive (1)'), (0, '#e3e3e3', 'Absent or incidental (0)')):
    vals = shares.loc[order, c].values * 100
    ax.barh([DIM_LABEL[d].replace('\n', ' ') for d in order], vals, left=left, color=col, label=lab)
    left += vals
ax.invert_yaxis(); ax.set_xlabel(f'Share of the {len(lit)} coded sources (%)'); ax.set_xlim(0, 100)
ax.legend(loc='lower right', ncol=1, frameon=True, fontsize=7)
ax.set_title('(a) Coverage of related precursor concepts')
ax = axes[1]
streams = lit.research_stream.value_counts().index.tolist()
short = {'Human factors & social engineering': 'Human factors & SE', 'AI/LLM security & governance': 'AI/LLM security & gov.',
         'Zero trust architecture': 'Zero trust architecture', 'GenAI & synthetic deception': 'GenAI & synthetic deception',
         'Adaptive/cognitive zero trust': 'Adaptive/cognitive ZT'}
M = lit.groupby('research_stream')[DIMS].mean().loc[streams]
im = ax.imshow(M.values, vmin=0, vmax=2, cmap='Blues', aspect='auto')
ax.set_xticks(range(len(DIMS))); ax.set_xticklabels([DIM_LABEL[d].replace('\n', ' ') for d in DIMS], rotation=30, ha='right')
ax.set_yticks(range(len(streams)))
ax.set_yticklabels([f'{short[s]} (n={int((lit.research_stream == s).sum())})' for s in streams])
for i in range(M.shape[0]):
    for j in range(M.shape[1]):
        ax.text(j, i, f'{M.values[i, j]:.2f}', ha='center', va='center', fontsize=7.5,
                color='white' if M.values[i, j] > 1.2 else 'black')
ax.set_title('(b) Mean code (0-2) by primary research stream')
fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
fig.tight_layout()
save(fig, 'Figure_04_Verification_Dimensions_Coverage.pdf')

# Fig 5: modalities (multi-label)
mods = lit.modalities.str.split('; ').explode().value_counts()
fig, ax = plt.subplots(figsize=(5.6, 2.5))
ax.bar(mods.index, mods.values, color=BLUE)
ax.set_ylabel('Sources (multi-label)'); ax.tick_params(axis='x', rotation=20)
ax.set_title('Attack and control modalities addressed by coded sources')
for i, v in enumerate(mods.values):
    ax.text(i, v + 0.4, str(v), ha='center', fontsize=7)
save(fig, 'Figure_05_Attack_Category_Distribution.pdf')
for k, v in mods.items():
    note(f'modality[{k}]', v)

# Figs 6 and 8: periods
bins = [0, 2009, 2019, 2023, 2026]
labels = ['1974-2009', '2010-2019', '2020-2023', '2024-2026']
lit['period'] = pd.cut(lit.year, bins=bins, labels=labels)
def stacked(col, title, name, colors=None):
    piv = pd.crosstab(lit.period, lit[col]).reindex(labels, fill_value=0)
    fig, ax = plt.subplots(figsize=(6.0, 2.9))
    bottom = np.zeros(len(piv))
    for c in piv.columns:
        ax.bar(piv.index.astype(str), piv[c].values, bottom=bottom, label=c)
        bottom += piv[c].values
    ax.set_ylabel('Sources'); ax.set_title(title)
    ax.legend(fontsize=7, loc='upper left', frameon=False)
    save(fig, name)
stacked('research_stream', 'Primary research stream by publication period', 'Figure_06_Research_Focus_Evolution.pdf')
stacked('source_type', 'Source type by publication period', 'Figure_08_Publication_Outlet_Trend.pdf')

# Fig 7: source types
st = lit.source_type.value_counts()
fig, ax = plt.subplots(figsize=(5.2, 2.5))
ax.bar(st.index, st.values, color=BLUE); ax.set_ylabel('Sources'); ax.tick_params(axis='x', rotation=20)
for i, v in enumerate(st.values):
    ax.text(i, v + 0.3, str(v), ha='center', fontsize=7)
ax.set_title(f'Source types in the coded corpus (N={len(lit)})')
save(fig, 'Figure_07_Source_Distribution.pdf')

# Fig 11: theoretical dependency matrix (not derived from data)
dep = pd.read_csv(DATA / 'dependency_matrix.csv', index_col=0)
fig, ax = plt.subplots(figsize=(4.0, 3.7))
im = ax.imshow(dep.values, vmin=0, vmax=3, cmap='Blues')
ax.set_xticks(range(7)); ax.set_xticklabels(dep.columns, fontsize=8, rotation=35, ha='right', rotation_mode='anchor')
ax.set_yticks(range(7)); ax.set_yticklabels(dep.index, fontsize=8)
for i in range(7):
    for j in range(7):
        ax.text(j, i, int(dep.values[i, j]), ha='center', va='center', fontsize=8,
                color='white' if dep.values[i, j] >= 2.5 else 'black')
fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, ticks=[0, 1, 2, 3]).set_label('0 none - 3 strong')
ax.set_title('Hypothesized ordinal dependency among constructs')
save(fig, 'Figure_11_Dependency_Matrix.pdf')

# ---------------------------------------------------------------- decision model and scenarios
par = pd.read_csv(DATA / 'decision_parameters.csv').set_index('symbol')['value'].to_dict()
sc = pd.read_csv(DATA / 'scenario_vignettes.csv')
EVID = ['provenance', 'context', 'authority', 'channel_integrity']
PRES = ['consequence', 'urgency', 'secrecy', 'novelty', 'irreversibility']
W0 = np.array([par['w_p'], par['w_c'], par['w_a'], par['w_h']])
V0 = np.array([par['v_q'], par['v_u'], par['v_s'], par['v_n'], par['v_i']])
CLASSES = ['Routine', 'Step-up / callback', 'Dual approval / hold', 'Reject / block']

def veto(df):
    f = df['flags'].fillna('')
    v1 = f.str.contains('cred')
    v2 = f.str.contains('priv') & ((df.provenance < 0.5) | (df.authority < 0.5))
    v3 = f.str.contains('payee') & (df.authority < 0.5) & ((df.urgency >= 0.5) | (df.secrecy >= 0.5))
    v4 = f.str.contains('data') & (df.channel_integrity < 0.5)
    rule = np.select([v1, v2, v3, v4], ['V1', 'V2', 'V3', 'V4'], default='')
    return (v1 | v2 | v3 | v4).astype(int).values, rule

def authority_floor(df):
    # Non-compensatory authority rule of Eq. (4): a high-consequence request (consequence >= q_high or any
    # protected-action flag) whose authority is below a_min is held for at least dual approval.
    high = (df.consequence >= par['q_high']) | (df['flags'].fillna('') != '')
    return ((df.authority < par['a_min']) & high).astype(int).values

def decide(A, R, M, F, tA, tR, tAlo, tRhi):
    return np.select([M == 1, F == 1, (A >= tA) & (R < tR), (A < tAlo) | (R >= tRhi)], [3, 2, 0, 2], default=1)

# All scores and weights are multiples of 0.05, so A and R are exact multiples of 0.0025.
# Rounding removes floating-point noise, so that boundary cases (e.g. R == tau_R) are decided by
# the declared inequalities of Eq. (4) and results are identical across platforms and library versions.
EPS_DECIMALS = 9
A = np.round(sc[EVID].values @ W0, EPS_DECIMALS)
R = np.round(sc[PRES].values @ V0, EPS_DECIMALS)
Mv, rule = veto(sc)
Fl = authority_floor(sc)
D = decide(A, R, Mv, Fl, par['tau_A'], par['tau_R'], par['tau_A_low'], par['tau_R_high'])
res = sc[['scenario_id', 'sector', 'originator', 'request_type', 'ground_truth']].copy()
res['assurance_A'] = A.round(4); res['pressure_R'] = R.round(4)
res['mandatory_veto_M'] = Mv; res['veto_rule'] = rule; res['authority_floor'] = Fl; res['decision'] = [CLASSES[d] for d in D]
res.to_csv(DATA / 'scenario_results.csv', index=False)

deceptive = (sc.ground_truth == 'deceptive').values
note('scenarios', len(sc)); note('legitimate', int((~deceptive).sum())); note('deceptive', int(deceptive.sum()))
for i, c in enumerate(CLASSES):
    note(f'class[{c}] legit/deceptive', f'{int(((D == i) & ~deceptive).sum())}/{int(((D == i) & deceptive).sum())}')
note('misses (deceptive routed Routine)', int(((D == 0) & deceptive).sum()))
note('legitimate-request escalations (legitimate not Routine)', int(((D != 0) & ~deceptive).sum()))
note('authority floor applied (not vetoed)', int(((Fl == 1) & (Mv == 0)).sum()))
note('vetoes by rule', pd.Series(rule[rule != '']).value_counts().to_dict())
for o in ['H2H', 'A2H', 'H2A', 'A2A']:
    m = (sc.originator == o).values
    note(f'originator[{o}] n / non-routine', f'{int(m.sum())} / {int((D[m] != 0).sum())}')

# Fig 12: scenario analysis
fig, axes = plt.subplots(2, 2, figsize=(7.0, 5.6))
ax = axes[0, 0]
mk = {0: 'o', 1: 's', 2: 'D', 3: 'X'}
for d in range(4):
    for truth, col in (('legitimate', BLUE), ('deceptive', RED)):
        m = (D == d) & (sc.ground_truth == truth).values
        ax.scatter(A[m], R[m], marker=mk[d], s=28, facecolor=col if truth == 'deceptive' else 'none',
                   edgecolor=col, linewidth=1)
ax.axvline(par['tau_A'], ls='--', c=GREY, lw=0.8); ax.axvline(par['tau_A_low'], ls=':', c=GREY, lw=0.8)
ax.axhline(par['tau_R'], ls='--', c=GREY, lw=0.8); ax.axhline(par['tau_R_high'], ls=':', c=GREY, lw=0.8)
ax.set_xlabel('Request assurance A(r)'); ax.set_ylabel('Consequence and pressure R(r)')
ax.set_xlim(0, 1.02); ax.set_ylim(0, 1.02)
ax.set_title('(a) Decision space (markers = decision)')
from matplotlib.lines import Line2D
h = [Line2D([], [], marker=mk[d], ls='', mec='k', mfc='none', label=CLASSES[d]) for d in range(4)]
h += [Line2D([], [], marker='o', ls='', mec=BLUE, mfc='none', label='Legitimate'),
      Line2D([], [], marker='o', ls='', mec=RED, mfc=RED, label='Deceptive')]
ax.legend(handles=h, fontsize=6.3, loc='lower left', frameon=True, ncol=1)
ax = axes[0, 1]
x = np.arange(4)
leg = [int(((D == i) & ~deceptive).sum()) for i in range(4)]
dec = [int(((D == i) & deceptive).sum()) for i in range(4)]
ax.bar(x, leg, color=BLUE, label='Legitimate'); ax.bar(x, dec, bottom=leg, color=RED, label='Deceptive')
ax.set_xticks(x); ax.set_xticklabels([c.replace(' / ', '/\n') for c in CLASSES])
ax.set_ylabel('Scenarios'); ax.set_ylim(0, 27); ax.legend(frameon=False); ax.set_title('(b) Decision by ground truth')
ax = axes[1, 0]
ors = ['H2H', 'A2H', 'H2A', 'A2A']
mat = np.array([[int(((D == i) & (sc.originator == o).values).sum()) for i in range(4)] for o in ors])
bottom = np.zeros(4)
cols = ['#cfe0f1', '#8fb3d9', ORANGE, RED]
for i in range(4):
    ax.bar(ors, mat[:, i], bottom=bottom, color=cols[i], label=CLASSES[i]); bottom += mat[:, i]
ax.set_ylabel('Scenarios'); ax.set_title('(c) Decision by request originator')
ax.legend(fontsize=6.3, frameon=False, loc='upper right')
ax = axes[1, 1]
secs = sc.sector.unique().tolist()
mat = np.array([[int(((D == i) & (sc.sector == s).values).sum()) for i in range(4)] for s in secs])
bottom = np.zeros(len(secs))
for i in range(4):
    ax.bar(secs, mat[:, i], bottom=bottom, color=cols[i]); bottom += mat[:, i]
ax.set_ylabel('Scenarios'); ax.tick_params(axis='x', rotation=25); ax.set_title('(d) Decision by sector')
fig.tight_layout()
save(fig, 'Figure_13_Scenario_Analysis.pdf')

# Sensitivity analysis (Fig 13)
rng = np.random.default_rng(2026)
tAs = np.round(np.arange(0.50, 0.9001, 0.025), 3)
tRs = np.round(np.arange(0.30, 0.7001, 0.025), 3)
ratio = par['c_h_over_c_d']
miss = np.zeros((len(tRs), len(tAs))); fesc = np.zeros_like(miss)
for i, tR in enumerate(tRs):
    for j, tA in enumerate(tAs):
        d = decide(A, R, Mv, Fl, tA, tR, min(par['tau_A_low'], tA), max(par['tau_R_high'], tR))
        miss[i, j] = ((d == 0) & deceptive).sum(); fesc[i, j] = ((d != 0) & ~deceptive).sum()
cost = ratio * miss + fesc
N = int(par['perturbation_draws']); kappa = par['dirichlet_concentration']
same = np.zeros(len(sc))
for _ in range(N):
    w = rng.dirichlet(kappa * W0 / W0.sum()); v = rng.dirichlet(kappa * V0 / V0.sum())
    d = decide(np.round(sc[EVID].values @ w, EPS_DECIMALS), np.round(sc[PRES].values @ v, EPS_DECIMALS), Mv, Fl, par['tau_A'], par['tau_R'], par['tau_A_low'], par['tau_R_high'])
    same += (d == D)
stab = same / N
res['weight_stability'] = stab.round(3)
res.to_csv(DATA / 'scenario_results.csv', index=False)
bi, bj = int(np.argmin(np.abs(tRs - par['tau_R']))), int(np.argmin(np.abs(tAs - par['tau_A'])))
note('base misses/legitimate escalations', f'{int(miss[bi, bj])}/{int(fesc[bi, bj])}')
note('grid misses range', f'{int(miss.min())}-{int(miss.max())}')
note('grid legitimate-escalation range', f'{int(fesc.min())}-{int(fesc.max())}')
imin = np.unravel_index(np.argmin(cost), cost.shape)
note('min-cost thresholds (first found)', f'tau_A={tAs[imin[1]]}, tau_R={tRs[imin[0]]}, cost={cost[imin]:.0f}, base cost={cost[bi, bj]:.0f}')
note('weight stability: share of scenarios with stability>=0.90', f'{(stab >= 0.9).mean():.3f}')
note('weight stability: mean', f'{stab.mean():.3f}')
note('weight stability: minimum (scenario)', f'{stab.min():.3f} ({res.scenario_id[np.argmin(stab)]})')
pd.DataFrame({'tau_R': np.repeat(tRs, len(tAs)), 'tau_A': np.tile(tAs, len(tRs)),
              'misses': miss.ravel().astype(int), 'legitimate_escalations': fesc.ravel().astype(int),
              'cost_ratio_%g' % ratio: cost.ravel()}).to_csv(DATA / 'sensitivity_summary.csv', index=False)

fig, axes = plt.subplots(1, 4, figsize=(6.4, 2.45), gridspec_kw={'width_ratios': [1, 1, 1, 1.15]})
ext = [tAs[0] - 0.0125, tAs[-1] + 0.0125, tRs[0] - 0.0125, tRs[-1] + 0.0125]
for ax, Z, t, cm in ((axes[0], miss, '(a) Missed deceptive', 'Reds'), (axes[1], fesc, '(b) Legitimate requests escalated', 'Blues'),
                     (axes[2], cost, rf'(c) Cost, $c_h/c_d$={ratio:g}', 'Purples')):
    im = ax.imshow(Z, origin='lower', extent=ext, aspect='auto', cmap=cm)
    ax.plot(par['tau_A'], par['tau_R'], marker='*', c='k', ms=8)
    ax.set_xlabel(r'$\tau_A$'); ax.set_title(t, fontsize=8)
    fig.colorbar(im, ax=ax, fraction=0.05, pad=0.03)
axes[0].set_ylabel(r'$\tau_R$')
for ax in axes[1:3]:
    ax.set_yticklabels([])
ax = axes[3]
ax.hist(stab * 100, bins=np.arange(40, 101, 5), color=GREEN)
ax.set_xlabel('Decision unchanged (%)'); ax.set_ylabel('Scenarios'); ax.set_title('(d) Weight perturbation', fontsize=8)
fig.tight_layout()
save(fig, 'Figure_14_Sensitivity_Analysis.pdf')

# ---------------------------------------------------------------- timing and overhead model
asm = pd.read_csv(DATA / 'analytical_assumptions.csv').set_index('symbol')['value'].to_dict()
Tj = np.array([asm['T_p'], asm['T_c'], asm['T_a'], asm['T_ch']])
Tpol, Taud, Thum = asm['T_policy'], asm['T_audit'], asm['T_human']
seq_k = [Tj[:k].sum() + Tpol + Taud for k in range(1, 5)]
par_k = [Tj[:k].max() + Tpol + Taud for k in range(1, 5)]
base = Tpol + Taud
note('machine sequential (4 checks) s', round(seq_k[-1], 2)); note('machine parallel (4 checks) s', round(par_k[-1], 2))
note('parallel gain', round(seq_k[-1] / par_k[-1], 2)); note('baseline policy+audit s', round(base, 2))
note('time saved over 1000 requests s', round(1000 * (seq_k[-1] - par_k[-1]), 1))
note('single-worker capacity req/s baseline/seq/par', f'{1/base:.2f}/{1/seq_k[-1]:.2f}/{1/par_k[-1]:.2f}')

fig, axes = plt.subplots(2, 2, figsize=(6.4, 4.6))
k = np.arange(1, 5)
axes[0, 0].plot(k, seq_k, marker='o', color=BLUE); axes[0, 0].set_title('(a) Sequential machine path')
axes[0, 1].plot(k, par_k, marker='s', color=ORANGE); axes[0, 1].set_title('(b) Parallel machine path')
for ax in axes[0]:
    ax.set_xticks(k); ax.set_ylim(0, 0.9); ax.set_xlabel('Enabled automated checks'); ax.set_ylabel('Latency (s)')
axes[1, 0].bar(k, np.array(seq_k) / np.array(par_k), color=GREEN); axes[1, 0].set_xticks(k)
axes[1, 0].set_xlabel('Enabled automated checks'); axes[1, 0].set_ylabel('Sequential / parallel'); axes[1, 0].set_title('(c) Parallelization gain')
axes[1, 1].bar(['Provenance', 'Context', 'Authority', 'Channel', 'Policy', 'Audit'], list(Tj) + [Tpol, Taud], color=BLUE)
axes[1, 1].tick_params(axis='x', rotation=35); axes[1, 1].set_ylabel('Assumed time (s)'); axes[1, 1].set_title('(d) Component contribution')
fig.tight_layout(); save(fig, 'Figure_15_Processing_Characteristics.pdf')

fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.4))
n = np.array([1, 10, 50, 100, 250, 500, 750, 1000])
axes[0].plot(n, n * base, marker='o', color=GREY, label='Baseline policy path')
axes[0].plot(n, n * seq_k[-1], marker='s', color=BLUE, label='Sequential CZT')
axes[0].plot(n, n * par_k[-1], marker='^', color=ORANGE, label='Parallel CZT')
axes[0].set_xlabel('Requests processed serially'); axes[0].set_ylabel('Cumulative machine time (s)')
axes[0].legend(frameon=False); axes[0].set_title('(a) Cumulative machine-path time')
axes[1].plot(n, n * (seq_k[-1] - par_k[-1]), marker='o', color=GREEN)
axes[1].set_xlabel('Requests processed serially'); axes[1].set_ylabel('Time saved (s)'); axes[1].set_title('(b) Saving from parallel checks')
axes[2].bar(['Baseline\npolicy', 'Sequential\nCZT', 'Parallel\nCZT'], [1 / base, 1 / seq_k[-1], 1 / par_k[-1]], color=[GREY, BLUE, ORANGE])
axes[2].set_ylabel('Requests per second'); axes[2].set_title('(c) Single-worker bound, 1/T')
fig.tight_layout(); save(fig, 'Figure_16_Latency_and_Scalability.pdf')

paths = ['Low', 'Medium', 'High']
pay = pd.DataFrame({'Provenance': [0, asm['M_p_med'], asm['M_p']], 'Context': [0, asm['M_c_med'], asm['M_c']],
                    'Authority': [0, asm['M_a_med'], asm['M_a']],
                    'Approval and audit': [asm['M_aa_low'], asm['M_aa_med'], asm['M_aa']]}, index=paths)
msgs = [asm['msg_low'], asm['msg_med'], asm['msg_high']]
appr = np.array([asm['k_human_low'], asm['k_human_med'], asm['k_human_high']])
e2e_seq = seq_k[-1] + appr * Thum; e2e_par = par_k[-1] + appr * Thum
for p_, t1, t2, pl in zip(paths, e2e_seq, e2e_par, pay.sum(axis=1)):
    note(f'path[{p_}] payload kB / e2e seq / e2e par', f'{pl:.1f} / {t1:.2f} / {t2:.2f}')
fig, axes = plt.subplots(2, 3, figsize=(7.0, 4.4))
axes[0, 0].bar(paths, pay.sum(axis=1), color=BLUE); axes[0, 0].set_ylabel('Payload (kB)'); axes[0, 0].set_title('(a) Evidence payload')
bottom = np.zeros(3)
for c, col in zip(pay.columns, [BLUE, ORANGE, GREEN, RED]):
    axes[0, 1].bar(paths, pay[c], bottom=bottom, color=col, label=c); bottom += pay[c].values
axes[0, 1].legend(fontsize=6, frameon=False, loc='upper left'); axes[0, 1].set_ylim(0, 19); axes[0, 1].set_ylabel('Payload (kB)'); axes[0, 1].set_title('(b) Payload composition')
axes[0, 2].bar(paths, msgs, color=BLUE); axes[0, 2].set_ylabel('Messages'); axes[0, 2].set_title('(c) Verification messages')
xx = np.arange(3); wdt = 0.38
axes[1, 0].bar(xx - wdt / 2, e2e_seq, wdt, color=BLUE, label='Sequential')
axes[1, 0].bar(xx + wdt / 2, e2e_par, wdt, color=ORANGE, label='Parallel')
axes[1, 0].set_yscale('log'); axes[1, 0].set_xticks(xx); axes[1, 0].set_xticklabels(paths)
axes[1, 0].set_ylabel('End-to-end time (s, log)'); axes[1, 0].set_ylim(0.1, 2000); axes[1, 0].legend(frameon=False, fontsize=6.3, loc='upper left', ncol=2); axes[1, 0].set_title('(d) End-to-end time')
axes[1, 1].bar(paths, appr, color=BLUE); axes[1, 1].set_ylabel('Human approvals'); axes[1, 1].set_yticks([0, 1, 2]); axes[1, 1].set_title('(e) Human operations')
th = np.array([10, 30, 45, 60, 120, 180, 300])
axes[1, 2].plot(th, par_k[-1] + th, marker='o', color=ORANGE, label='Medium (1 approval)')
axes[1, 2].plot(th, par_k[-1] + 2 * th, marker='s', color=RED, label='High (2 approvals)')
axes[1, 2].axvline(Thum, ls=':', c=GREY); axes[1, 2].set_xlabel(r'Assumed $T_{human}$ (s)'); axes[1, 2].set_ylabel('End-to-end time (s)')
axes[1, 2].legend(frameon=False, fontsize=6.3); axes[1, 2].set_title('(f) Sensitivity to human time')
fig.tight_layout(); save(fig, 'Figure_17_Overhead_and_Runtime.pdf')

(DATA / 'derived_numbers.txt').write_text('\n'.join(out_numbers) + '\n', encoding='utf-8')
print('\n'.join(out_numbers))
