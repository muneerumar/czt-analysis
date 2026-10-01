from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parents[1] / 'data'
DIMS = ['provenance', 'context', 'authority', 'channel', 'friction', 'challenge', 'feedback']


def test_matrix_integrity():
    m = pd.read_csv(DATA / 'literature_coding_matrix.csv')
    assert len(m) == 66 and m.key.is_unique
    assert not {'ref51', 'ref52', 'ref94'} & set(m.key)
    assert m[DIMS].isin([0, 1, 2]).all().all()
    nonzero = m[DIMS].sum(axis=1) > 0
    assert m.loc[nonzero, 'coding_justification'].fillna('').str.len().gt(10).all()
    assert m.source_type.value_counts().to_dict() == {'Journal article': 26, 'Standard/report': 20, 'Conference paper': 15,
                                                     'Book/chapter': 3, 'Preprint': 2}


def test_authoritative_and_generated_matrix_agree():
    a = pd.read_csv(DATA / 'literature_coding_matrix_authoritative.csv').set_index('key').sort_index()
    b = pd.read_csv(DATA / 'literature_coding_matrix.csv').set_index('key').sort_index()
    assert (a[DIMS] == b[DIMS]).all().all()
