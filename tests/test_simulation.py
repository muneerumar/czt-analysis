"""Checks for the Monte Carlo simulation in sim/."""
import subprocess, sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'sim'))
import model  # noqa: E402

LEVEL = {'Routine': 0, 'Step-up / callback': 1, 'Dual approval / hold': 2, 'Reject / block': 3}


def test_simulation_decision_rule_matches_released_scenarios():
    """The simulator's CZT decision (Eqs. 1-4, V1-V4) reproduces all 60 released scenario decisions."""
    sc = pd.read_csv(ROOT / 'data' / 'scenario_vignettes.csv')
    res = pd.read_csv(ROOT / 'data' / 'scenario_results.csv').set_index('scenario_id')
    f = sc['flags'].fillna('')
    st = model.Stream(cls=np.zeros(len(sc), int), media=np.zeros(len(sc), bool), p=sc.provenance.values, c=sc.context.values,
                      c_poisoned=np.zeros(len(sc), bool), a=sc.authority.values, h=sc.channel_integrity.values,
                      q=sc.consequence.values, u=sc.urgency.values, s=sc.secrecy.values, n=sc.novelty.values,
                      i=sc.irreversibility.values, cred=f.str.contains('cred').values, priv=f.str.contains('priv').values,
                      payee=f.str.contains('payee').values, data=f.str.contains('data').values, rand=np.zeros((len(sc), 8)))
    obs = {'p': st.p, 'c': st.c, 'a': st.a, 'h': st.h, 'n': st.n}
    D = model.czt_decision(st, obs, model.TAU, no_friction=False)
    expected = res.loc[sc.scenario_id, 'decision'].map(LEVEL).values
    assert (D == expected).all()


def test_replication_is_deterministic():
    P = model.load_params(); P['n_periods'] = 2
    a = model.replicate(P, seed=7); b = model.replicate(P, seed=7)
    for cfg in model.CONFIGS:
        assert a[cfg][0] == b[cfg][0]


def test_perfect_evidence_blocks_spoofing():
    """With perfect, complete, unpoisoned evidence, spoofed-sender attacks (A1) almost never succeed under CZT."""
    P = model.load_params()
    P.update(n_periods=3, check_error=0.0, provenance_coverage=1.0, poison_success=0.0, attack_share=0.2)
    out = model.replicate(P, seed=3, configs=['ZT baseline', 'CZT (full)'])
    a1 = model.CLASSES.index('A1')
    assert out['CZT (full)'][1][a1] <= 0.05 * max(1, out['ZT baseline'][1][a1])


def test_run_simulation_quick():
    r = subprocess.run([sys.executable, str(ROOT / 'sim' / 'run_simulation.py'), '--quick'], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
