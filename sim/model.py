"""Monte Carlo simulation of communication-request handling under alternative defenses.

The model generates organizational request streams containing legitimate requests and deceptive requests from the
five adversary classes of the threat model (A1 spoofed sender, A2 compromised account, A3 insider, A4 synthetic
meeting participant, A5 manipulated agent), and compares how each defense configuration handles the same stream
(common random numbers). CZT decisions use Eqs. (1)-(4) and vetoes V1-V4 of the article on *observed* evidence,
which is noisy, incomplete (provenance coverage < 1) and can be poisoned by A2/A3 attackers.

This is a simulation under stated assumptions (see parameters.json), not an empirical evaluation.
"""
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
LEVELS = {  # rubric levels (data/scoring_rubric.csv)
    'p': np.array([0.1, 0.25, 0.5, 0.75, 1.0]), 'c': np.array([0.25, 0.5, 0.75, 1.0]),
    'a': np.array([0.0, 0.25, 0.5, 0.75, 1.0]), 'h': np.array([0.25, 0.5, 0.75, 1.0]),
    'n': np.array([0.0, 0.5, 1.0]),
}
W = np.array([0.25, 0.25, 0.25, 0.25])                  # w_p, w_c, w_a, w_h  (Table 8)
V = np.array([0.30, 0.15, 0.15, 0.20, 0.20])            # v_q, v_u, v_s, v_n, v_i
TAU = dict(tau_A=0.70, tau_R=0.50, tau_A_low=0.40, tau_R_high=0.70)
A_MIN, Q_HIGH = 0.5, 0.6                                # authority floor (Eq. 4)
CLASSES = ['routine', 'legit_high', 'A1', 'A2', 'A3', 'A4', 'A5']
CONFIGS = ['ZT baseline', 'Awareness training', 'Uniform callback', 'CZT (full)',
           'CZT - provenance', 'CZT - context', 'CZT - authority', 'CZT - channel',
           'CZT - friction', 'CZT - human challenge', 'CZT - feedback']


def load_params(path: Path = HERE / 'parameters.json') -> dict:
    raw = json.loads(path.read_text(encoding='utf-8'))
    return {k: v['value'] for k, v in raw.items() if not k.startswith('_')}


def _pick(rng, n, values, probs):
    return rng.choice(np.asarray(values, float), size=n, p=np.asarray(probs, float))


@dataclass
class Stream:
    cls: np.ndarray; media: np.ndarray
    p: np.ndarray; c: np.ndarray; c_poisoned: np.ndarray; a: np.ndarray; h: np.ndarray
    q: np.ndarray; u: np.ndarray; s: np.ndarray; n: np.ndarray; i: np.ndarray
    cred: np.ndarray; priv: np.ndarray; payee: np.ndarray; data: np.ndarray
    rand: np.ndarray            # uniforms for outcome draws, shared across configurations


def generate(rng: np.random.Generator, n: int, P: dict) -> Stream:
    """One period of requests. Attribute distributions follow the threat model (Table 6)."""
    mix = P['attack_mix']
    probs = [(1 - P['attack_share']) * (1 - P['share_high_consequence']),
             (1 - P['attack_share']) * P['share_high_consequence']] + [P['attack_share'] * mix[k] for k in ['A1', 'A2', 'A3', 'A4', 'A5']]
    cls = rng.choice(len(CLASSES), size=n, p=np.array(probs) / sum(probs))
    z = lambda: np.zeros(n)
    p, c, a, h, q, u, s, nv, i = (z() for _ in range(9))
    media = np.zeros(n, bool); flags = {f: np.zeros(n, bool) for f in ['cred', 'priv', 'payee', 'data']}

    def setv(mask, **kw):
        m = int(mask.sum())
        if m == 0: return
        for name, (vals, pr) in kw.items():
            {'p': p, 'c': c, 'a': a, 'h': h, 'q': q, 'u': u, 's': s, 'n': nv, 'i': i}[name][mask] = _pick(rng, m, vals, pr)

    def setflags(mask, pr):   # mutually exclusive request flags; remaining probability = no flag
        m = int(mask.sum())
        if m == 0: return
        names = list(pr); weights = list(pr.values()) + [max(0.0, 1 - sum(pr.values()))]
        k = rng.choice(len(names) + 1, size=m, p=np.array(weights) / sum(weights))
        idx = np.flatnonzero(mask)
        for j, f in enumerate(names): flags[f][idx[k == j]] = True

    m = cls == 0  # legitimate routine
    setv(m, p=([1, .75], [.6, .4]), c=([1, .75, .5], [.85, .1, .05]), a=([1, .75], [.7, .3]), h=([1, .75], [.9, .1]),
         q=([.1, .3], [.6, .4]), u=([0, .5], [.8, .2]), s=([0], [1]), n=([0, .5], [.8, .2]), i=([0, .5], [.6, .4]))
    m = cls == 1  # legitimate high-consequence
    setv(m, p=([1, .75], [.6, .4]), c=([1, .75, .5], [.7, .2, .1]), a=([1, .75], [.6, .4]), h=([1, .75], [.85, .15]),
         q=([.6, .8, 1], [.4, .4, .2]), u=([0, .5, 1], [.4, .4, .2]), s=([0, .5], [.9, .1]), n=([0, .5, 1], [.4, .4, .2]), i=([.5, 1], [.5, .5]))
    setflags(m, {'payee': .2, 'priv': .25, 'data': .15})
    m = cls == 2  # A1 spoofed sender (20% by cloned voice)
    setv(m, p=([.25, .1], [.8, .2]), c=([.25], [1]), a=([.25, .5], [.5, .5]), h=([.25, .5, .75], [.4, .3, .3]),
         q=([.8, 1], [.5, .5]), u=([.5, 1], [.5, .5]), s=([0, .5, 1], [.3, .4, .3]), n=([1], [1]), i=([.5, 1], [.3, .7]))
    media[m] = rng.random(int(m.sum())) < 0.2
    setflags(m, {'payee': .45, 'cred': .3, 'data': .15, 'priv': .1})
    m = cls == 3  # A2 compromised legitimate account
    setv(m, p=([.75], [1]), c=([.25, .5], [.5, .5]), a=([1, .5], [.3, .7]), h=([1, .75], [.6, .4]),
         q=([.6, .8, 1], [.3, .4, .3]), u=([.5, 1], [.6, .4]), s=([0, .5], [.6, .4]), n=([.5, 1], [.3, .7]), i=([.5, 1], [.4, .6]))
    setflags(m, {'payee': .5, 'data': .25, 'priv': .25})
    m = cls == 4  # A3 malicious insider
    setv(m, p=([1], [1]), c=([.25, .5], [.5, .5]), a=([1, .5], [.5, .5]), h=([1], [1]),
         q=([.6, .8, 1], [.3, .4, .3]), u=([0, .5], [.5, .5]), s=([0, .5], [.5, .5]), n=([.5, 1], [.4, .6]), i=([.5, 1], [.4, .6]))
    setflags(m, {'data': .5, 'payee': .3, 'priv': .2})
    m = cls == 5  # A4 synthetic meeting participant
    setv(m, p=([.1, .5], [.7, .3]), c=([.25], [1]), a=([.25, .5], [.5, .5]), h=([.5], [1]),
         q=([.8, 1], [.3, .7]), u=([1], [1]), s=([.5, 1], [.4, .6]), n=([1], [1]), i=([1], [1]))
    media[m] = True
    setflags(m, {'payee': .8, 'data': .2})
    m = cls == 6  # A5 manipulated agent (taint rule: provenance of influencing inputs)
    setv(m, p=([.25, .5], [.5, .5]), c=([.25, .5], [.6, .4]), a=([0, .25], [.7, .3]), h=([.75, .5], [.6, .4]),
         q=([.6, .8, 1], [.3, .4, .3]), u=([0, .5], [.5, .5]), s=([0, .5], [.6, .4]), n=([1], [1]), i=([.5, 1], [.5, .5]))
    setflags(m, {'priv': .4, 'data': .3, 'cred': .3})
    poisoned = np.isin(cls, [3, 4]) & (rng.random(n) < P['poison_success'])
    return Stream(cls, media, p, c, poisoned, a, h, q, u, s, nv, i, flags['cred'], flags['priv'], flags['payee'], flags['data'],
                  rng.random((n, 8)))


def observe(st: Stream, rng: np.random.Generator, P: dict, drop: str | None):
    """Evidence as seen by the CZT checks: noisy, incomplete, and possibly poisoned."""
    n = len(st.cls)
    obs = {}
    for key, true in [('p', st.p), ('c', np.where(st.c_poisoned, 1.0, st.c)), ('a', st.a), ('h', st.h), ('n', st.n)]:
        err = rng.random(n) < P['check_error']
        obs[key] = np.where(err, rng.choice(LEVELS[key], size=n), true)
    no_prov = rng.random(n) >= P['provenance_coverage']
    obs['p'] = np.where(no_prov, 0.5, obs['p'])                        # provenance unknown on this channel
    dropmap = {'CZT - provenance': 'p', 'CZT - context': 'c', 'CZT - authority': 'a', 'CZT - channel': 'h'}
    if drop in dropmap: obs[dropmap[drop]] = np.full(n, 0.5)           # construct removed: evidence uninformative
    return obs


def czt_decision(st: Stream, obs: dict, tau: dict, no_friction: bool) -> np.ndarray:
    A = np.round(np.column_stack([obs['p'], obs['c'], obs['a'], obs['h']]) @ W, 9)
    R = np.round(np.column_stack([st.q, st.u, st.s, obs['n'], st.i]) @ V, 9)
    M = (st.cred | (st.priv & ((obs['p'] < .5) | (obs['a'] < .5))) |
         (st.payee & (obs['a'] < .5) & ((st.u >= .5) | (st.s >= .5))) | (st.data & (obs['h'] < .5)))
    high = (st.q >= Q_HIGH) | st.cred | st.priv | st.payee | st.data
    F = (obs['a'] < A_MIN) & high                                     # authority floor (Eq. 4)
    D = np.select([M, F, (A >= tau['tau_A']) & (R < tau['tau_R']), (A < tau['tau_A_low']) | (R >= tau['tau_R_high'])], [3, 2, 0, 2], 1)
    if no_friction:
        D = np.where(D == 3, 3, 0)
    return D


def outcomes(st: Stream, D: np.ndarray, P: dict, detect_boost: float, act: float):
    """Returns harm (deceptive request executed) and delay cost per request, given control levels D (0-3)."""
    deceptive = st.cls >= 2
    insider = st.cls == 4
    detect = np.where(st.media, P['human_detect_media'], P['human_detect_text'])
    detect = detect + (1 - detect) * detect_boost
    cb = np.where(insider, P['callback_catch_insider'], P['callback_catch'])
    r = st.rand
    doubt_acted = (r[:, 0] < detect) & (r[:, 1] < act)
    caught_cb = r[:, 2] < cb
    caught_dual = caught_cb | (r[:, 3] < P['dual_catch'])
    stopped = np.select([D == 3, D == 2, D == 1], [np.ones_like(caught_cb), caught_dual, caught_cb],
                        doubt_acted & caught_cb)
    harm = deceptive & ~stopped
    legit = ~deceptive
    delay = np.where(legit, np.select([D == 1, D == 2, D == 3], [1.0, 2.0, 3.0], 0.0), 0.0)
    delay = delay + np.where(legit & (D == 0) & (r[:, 4] < P['false_refusal_legit']), 1.0, 0.0)
    return harm, delay


def run_config(config: str, streams: list, P: dict, seed: int):
    """Runs one configuration over all periods of one replication. Returns per-class counts and totals."""
    rng = np.random.default_rng(seed)       # observation noise; same seed for every configuration
    tau = dict(TAU)
    tot = dict(requests=0, harm=0, delay=0.0, legit=0, legit_escalated=0, deceptive=0)
    harm_by_class = np.zeros(len(CLASSES))
    for st in streams:
        n = len(st.cls)
        if config == 'ZT baseline':
            D = np.zeros(n, int); boost, act = 0.0, P['act_on_doubt']
        elif config == 'Awareness training':
            D = np.zeros(n, int); boost, act = P['training_effect'], P['act_on_doubt']
        elif config == 'Uniform callback':
            D = np.where(st.q >= 0.6, 1, 0); boost, act = 0.0, P['act_on_doubt']
        else:
            obs = observe(st, rng, P, config)
            D = czt_decision(st, obs, tau, no_friction=(config == 'CZT - friction'))
            boost = 0.0
            act = min(1.0, P['act_on_doubt'] + (0.0 if config == 'CZT - human challenge' else P['challenge_uplift']))
        harm, delay = outcomes(st, D, P, boost, act)
        legit = st.cls < 2
        tot['requests'] += n; tot['harm'] += int(harm.sum()); tot['delay'] += float(delay.sum())
        tot['legit'] += int(legit.sum()); tot['legit_escalated'] += int((legit & (D > 0)).sum()); tot['deceptive'] += int((~legit).sum())
        harm_by_class += np.bincount(st.cls[harm], minlength=len(CLASSES))
        if config.startswith('CZT') and config != 'CZT - feedback':      # Eq. (6) recalibration between periods
            # Observable feedback: f_I = discovered incidents / (discovered incidents + stopped attempts);
            # f_E = share of legitimate requests escalated (interruption rate). Vetoes and the authority floor
            # are not recalibrated. Thresholds keep tau_A_low <= tau_A and tau_R <= tau_R_high.
            found = int((harm & (st.rand[:, 5] < P['post_hoc_detection'])).sum())
            stopped = int(((st.cls >= 2) & ~harm & (D > 0)).sum())
            f_fn = found / max(1, found + stopped)
            f_fp = (legit & (D > 0)).sum() / max(1, legit.sum())
            step = P['eta'] * (f_fn - f_fp)
            tau['tau_A'] = float(np.clip(tau['tau_A'] + step, 0, 1)); tau['tau_R'] = float(np.clip(tau['tau_R'] - step, 0, 1))
            tau['tau_A_low'] = min(tau['tau_A_low'], tau['tau_A']); tau['tau_R_high'] = max(tau['tau_R_high'], tau['tau_R'])
    tot['cost'] = P['c_h_over_c_d'] * tot['harm'] + tot['delay']
    return tot, harm_by_class


def replicate(P: dict, seed: int, configs=CONFIGS):
    rng = np.random.default_rng(seed)
    streams = [generate(rng, P['requests_per_period'], P) for _ in range(P['n_periods'])]
    return {cfg: run_config(cfg, streams, P, seed + 10_000) for cfg in configs}
