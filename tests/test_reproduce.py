"""Re-runs the full pipeline in a temporary copy and checks it reproduces every released number."""
import shutil, subprocess, sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_pipeline_reproduces_released_outputs(tmp_path):
    work = tmp_path / 'repo'
    shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns('.git', '__pycache__', '.pytest_cache'))
    subprocess.run([sys.executable, 'tools/build_coding_matrix.py'], cwd=work, check=True)
    subprocess.run([sys.executable, 'tools/build_scenarios.py'], cwd=work, check=True, capture_output=True)
    subprocess.run([sys.executable, 'generate_figures.py'], cwd=work, check=True, capture_output=True)
    ref = (ROOT / 'data' / 'derived_numbers.txt').read_text(encoding='utf-8').replace('\r', '')
    new = (work / 'data' / 'derived_numbers.txt').read_text(encoding='utf-8').replace('\r', '')
    assert new == ref
    for name in ['scenario_results.csv', 'sensitivity_summary.csv', 'literature_coding_matrix.csv', 'scenario_vignettes.csv']:
        a = pd.read_csv(ROOT / 'data' / name); b = pd.read_csv(work / 'data' / name)
        pd.testing.assert_frame_equal(a, b, check_exact=False, atol=1e-6)
