"""Independent re-implementation of Eqs. (1)-(4) and the veto rules V1-V4, checked against the released results."""
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
LEVEL = {'Routine': 0, 'Step-up / callback': 1, 'Dual approval / hold': 2, 'Reject / block': 3}


@pytest.fixture(scope='module')
def inputs():
    sc = pd.read_csv(DATA / 'scenario_vignettes.csv')
    par = pd.read_csv(DATA / 'decision_parameters.csv').set_index('symbol')['value'].to_dict()
    res = pd.read_csv(DATA / 'scenario_results.csv')
    return sc, par, res


def veto(row):
    f = row.flags if isinstance(row.flags, str) else ''
    if 'cred' in f:
        return 'V1'
    if 'priv' in f and (row.provenance < 0.5 or row.authority < 0.5):
        return 'V2'
    if 'payee' in f and row.authority < 0.5 and (row.urgency >= 0.5 or row.secrecy >= 0.5):
        return 'V3'
    if 'data' in f and row.channel_integrity < 0.5:
        return 'V4'
    return ''


def floor(row, p):
    f = row.flags if isinstance(row.flags, str) else ''
    return row.authority < p['a_min'] and (row.consequence >= p['q_high'] or f != '')


def decide(A, R, M, p, F=False):
    if M:
        return 3
    if F:
        return 2
    if A >= p['tau_A'] and R < p['tau_R']:
        return 0
    if A < p['tau_A_low'] or R >= p['tau_R_high']:
        return 2
    return 1


def test_weights_sum_to_one(inputs):
    _, p, _ = inputs
    assert abs(p['w_p'] + p['w_c'] + p['w_a'] + p['w_h'] - 1) < 1e-12
    assert abs(p['v_q'] + p['v_u'] + p['v_s'] + p['v_n'] + p['v_i'] - 1) < 1e-12


def test_released_results_match_independent_implementation(inputs):
    sc, p, res = inputs
    res = res.set_index('scenario_id')
    for row in sc.itertuples():
        A = round(p['w_p'] * row.provenance + p['w_c'] * row.context + p['w_a'] * row.authority + p['w_h'] * row.channel_integrity, 9)
        R = round(p['v_q'] * row.consequence + p['v_u'] * row.urgency + p['v_s'] * row.secrecy + p['v_n'] * row.novelty + p['v_i'] * row.irreversibility, 9)
        rule = veto(row)
        r = res.loc[row.scenario_id]
        assert abs(r.assurance_A - A) < 1e-4 and abs(r.pressure_R - R) < 1e-4
        assert (r.veto_rule if isinstance(r.veto_rule, str) else '') == rule
        assert LEVEL[r.decision] == decide(A, R, bool(rule), p, floor(row, p)), row.scenario_id


def test_veto_takes_precedence_and_boundaries(inputs):
    _, p, _ = inputs
    assert decide(1.0, 0.0, True, p) == 3                  # veto overrides high assurance
    assert decide(p['tau_A'], p['tau_R'] - 0.0025, False, p) == 0
    assert decide(p['tau_A'], p['tau_R'], False, p) == 1    # R == tau_R is not routine (strict inequality)
    assert decide(p['tau_A_low'] - 0.0025, 0.0, False, p) == 2
    assert decide(0.9, p['tau_R_high'], False, p) == 2


def test_authority_floor_blocks_compensation(inputs):
    # Audit case: calm payee change, strong provenance/context/channel, no authority.
    _, p, _ = inputs
    row = pd.Series(dict(flags='payee', provenance=1, context=1, authority=0, channel_integrity=1,
                         consequence=0.6, urgency=0, secrecy=0, novelty=1, irreversibility=0.5))
    A = 0.25 * (1 + 1 + 0 + 1); R = round(0.3 * 0.6 + 0.2 * 1 + 0.2 * 0.5, 9)
    assert A >= p['tau_A'] and R < p['tau_R']            # would be routine without the floor
    assert veto(row) == ''                               # no veto (no urgency or secrecy)
    assert decide(A, R, False, p, floor(row, p)) == 2    # authority floor: at least dual approval


def test_reported_headline_counts(inputs):
    sc, _, res = inputs
    m = res.merge(sc[['scenario_id', 'ground_truth']], on='scenario_id', suffixes=('', '_v'))
    assert len(m) == 60 and (m.ground_truth == 'deceptive').sum() == 30
    assert ((m.decision == 'Routine') & (m.ground_truth == 'deceptive')).sum() == 0
    assert ((m.decision != 'Routine') & (m.ground_truth == 'legitimate')).sum() == 6
