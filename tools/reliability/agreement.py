"""Recomputes the second-coder agreement statistics reported in Section 3.4 from data/second_coder_codes.csv.

Codes are the original (pre-resolution) codes of the first coder and the blind second coder on the 21-source sample
drawn by build_kit.py (stratified by research stream, random seed 2026; keys in sample_keys.csv).
Linear weighted Cohen's kappa is implemented directly (no sklearn). A bootstrap over sources gives a 95% interval
for the mean kappa across the seven dimensions.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DIMS = ['provenance', 'context', 'authority', 'channel', 'friction', 'challenge', 'feedback']


def weighted_kappa(a, b, k=3):
    a, b = np.asarray(a, int), np.asarray(b, int)
    O = np.zeros((k, k))
    for x, y in zip(a, b):
        O[x, y] += 1
    O /= O.sum()
    E = np.outer(O.sum(1), O.sum(0))
    W = np.abs(np.subtract.outer(np.arange(k), np.arange(k))) / (k - 1)
    den = (W * E).sum()
    return 1.0 if den == 0 else 1 - (W * O).sum() / den


def stats(df):
    ex = np.mean([(df[f'{d}_first'] == df[f'{d}_second']).mean() for d in DIMS])
    ks = {d: weighted_kappa(df[f'{d}_first'], df[f'{d}_second']) for d in DIMS}
    agree = sum(int((df[f'{d}_first'] == df[f'{d}_second']).sum()) for d in DIMS)
    return agree, ex, ks


if __name__ == '__main__':
    df = pd.read_csv(ROOT / 'data' / 'second_coder_codes.csv')
    agree, _, ks = stats(df)
    n = len(df) * len(DIMS)
    print(f'sources: {len(df)}; exact agreement: {agree}/{n} = {agree / n:.4f}')
    for d, k in ks.items():
        print(f'  kappa[{d}] = {k:.3f}')
    print(f'mean kappa = {np.mean(list(ks.values())):.3f}')
    rng = np.random.default_rng(2026)
    boot = []
    for _ in range(5000):
        s = df.iloc[rng.integers(0, len(df), len(df))]
        boot.append(np.mean(list(stats(s)[2].values())))
    lo, hi = np.percentile(boot, [2.5, 97.5])
    print(f'bootstrap 95% interval of mean kappa (5000 resamples of sources): {lo:.2f}-{hi:.2f}')
