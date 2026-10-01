"""Builds the blank workbooks of the CZT reliability kit from the released data (run once)."""
import sys, pathlib, random
import pandas as pd
from openpyxl import Workbook
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.styles import Font, Alignment, PatternFill

SRC = pathlib.Path(sys.argv[1])          # path to the manuscript source folder (contains data/)
OUT = pathlib.Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
HDR = Font(bold=True); WRAP = Alignment(wrap_text=True, vertical='top'); FILL = PatternFill('solid', fgColor='FFF2CC')

def sheet_from_rows(ws, header, rows, widths):
    ws.append(header)
    for c in ws[1]: c.font = HDR; c.alignment = WRAP
    for r in rows: ws.append(r)
    for i, w in enumerate(widths): ws.column_dimensions[chr(65 + i)].width = w
    for row in ws.iter_rows(min_row=2):
        for c in row: c.alignment = WRAP
    ws.freeze_panes = 'A2'

# ---------------- 1. second coder (blind), stratified 30% sample
lit = pd.read_csv(SRC / 'data' / 'literature_coding_matrix.csv')
random.seed(2026)
sample = []
for stream, g in lit.groupby('research_stream'):
    k = max(1, round(len(g) * 20 / len(lit)))
    sample += random.sample(sorted(g.key), min(k, len(g)))
sample = sorted(sample, key=lambda s: int(s[3:]))
pd.DataFrame({'key': sample}).to_csv(OUT / '1_second_coder' / 'sample_keys.csv' if (OUT / '1_second_coder').mkdir(exist_ok=True) or True else None, index=False)
wb = Workbook(); ws = wb.active; ws.title = 'Instructions'
for line in [
    'SECOND-CODER RELIABILITY CHECK (blind)',
    'Code each source independently using the Codebook sheet. Do NOT look at literature_coding_matrix.csv or discuss codes with the first coder until you have finished.',
    'For each of the seven dimensions enter 0, 1 or 2 (dropdown). Ambiguous cases take the lower code.',
    'Use the "evidence" column to note the passage or feature your code rests on (short phrase is enough).',
    'Coder must be an author who did not draft the original codes. Record your name and the date on the Coding sheet.',
    'When finished, save the file and run: python scripts/analyze_reliability.py (see README).']:
    ws.append([line])
ws.column_dimensions['A'].width = 140
cb = wb.create_sheet('Codebook')
cbtext = (SRC / 'data' / 'coding_codebook.md').read_text(encoding='utf-8')
for line in cbtext.splitlines(): cb.append([line])
cb.column_dimensions['A'].width = 160
wsC = wb.create_sheet('Coding')
dims = ['provenance', 'context', 'authority', 'channel', 'friction', 'challenge', 'feedback']
wsC.append(['coder_name:', '', 'date:', ''])
header = ['key', 'short_cite', 'reference'] + dims + ['evidence / notes']
rows = [[k, lit.set_index('key').loc[k, 'short_cite'], lit.set_index('key').loc[k, 'reference']] + [''] * 7 + [''] for k in sample]
wsC.append(header)
for c in wsC[2]: c.font = HDR
for r in rows: wsC.append(r)
dv = DataValidation(type='list', formula1='"0,1,2"', allow_blank=False); wsC.add_data_validation(dv)
for col in 'DEFGHIJ':
    dv.add(f'{col}3:{col}{2 + len(rows)}')
    for r in range(3, 3 + len(rows)): wsC[f'{col}{r}'].fill = FILL
for col, w in zip('ABCDEFGHIJK', [8, 26, 70, 11, 9, 9, 9, 9, 9, 9, 40]): wsC.column_dimensions[col].width = w
for row in wsC.iter_rows(min_row=3):
    for c in row: c.alignment = WRAP
wsC.freeze_panes = 'D3'
wb.save(OUT / '1_second_coder' / 'second_coder_workbook.xlsx')

# ---------------- 2. independent scenario raters (blind to author scores and ground truth)
sc = pd.read_csv(SRC / 'data' / 'scenario_vignettes.csv')
rub = pd.read_csv(SRC / 'data' / 'scoring_rubric.csv')
VARS = [('provenance', 'p'), ('context', 'c'), ('authority', 'a'), ('channel_integrity', 'h'), ('consequence', 'q'),
        ('urgency', 'u'), ('secrecy', 's'), ('novelty', 'n'), ('irreversibility', 'i')]
(OUT / '2_scenario_raters').mkdir(exist_ok=True)
order = sc.sample(frac=1, random_state=7).scenario_id.tolist()   # shuffled so sector blocks do not cue ratings
for rater in ['A', 'B']:
    wb = Workbook(); ws = wb.active; ws.title = 'Instructions'
    for line in [
        f'INDEPENDENT SCENARIO RATING — Rater {rater}',
        'Score every vignette on the nine variables using ONLY the facts in the vignette, channel and request type, and the anchors on the Rubric sheet.',
        'Choose the nearest anchor level from the dropdown. Do not consult the authors\' scores, the ground-truth labels, or the other rater.',
        'Raters should not have written the vignettes. Record your name, role and the date on the Rating sheet.',
        'Expected time: about 2 hours for 60 vignettes.']:
        ws.append([line])
    ws.column_dimensions['A'].width = 140
    wr = wb.create_sheet('Rubric')
    sheet_from_rows(wr, ['variable', 'level', 'anchor'], rub.values.tolist(), [10, 8, 120])
    wsR = wb.create_sheet('Rating')
    wsR.append(['rater_name:', '', 'role:', '', 'date:', ''])
    head = ['scenario_id', 'sector', 'channel', 'request_type', 'vignette'] + [v for v, _ in VARS] + ['comment']
    wsR.append(head)
    for c in wsR[2]: c.font = HDR
    s2 = sc.set_index('scenario_id')
    for sid in order:
        r = s2.loc[sid]
        wsR.append([sid, r.sector, r.channel, r.request_type, r.vignette] + [''] * 9 + [''])
    for j, (v, code) in enumerate(VARS):
        levels = ','.join(str(x).rstrip('0').rstrip('.') if '.' in str(x) else str(x) for x in sorted(rub[rub.variable == code].level))
        col = chr(ord('F') + j)
        dv = DataValidation(type='list', formula1=f'"{levels}"', allow_blank=False); wsR.add_data_validation(dv)
        dv.add(f'{col}3:{col}{2 + len(order)}')
        for rr in range(3, 3 + len(order)): wsR[f'{col}{rr}'].fill = FILL
    for col, w in zip('ABCDEFGHIJKLMNO', [9, 11, 18, 20, 60] + [11] * 9 + [30]): wsR.column_dimensions[col].width = w
    for row in wsR.iter_rows(min_row=3):
        for c in row: c.alignment = WRAP
    wsR.freeze_panes = 'F3'
    wb.save(OUT / '2_scenario_raters' / f'scenario_rater_{rater}.xlsx')

# ---------------- 3. screening workbook for the 576 records that could not be excluded at title level
scr_path = SRC / 'data' / 'revision_stage_screening_log.csv'
if scr_path.exists():
    scr = pd.read_csv(scr_path)
    todo = scr[scr['exclusion_code'].astype(str).str.contains('FT-NA') & scr['decision_scope'].isna()]
    (OUT / '3_screening').mkdir(exist_ok=True)
    wb = Workbook(); ws = wb.active; ws.title = 'Instructions'
    for line in [
        'TITLE/ABSTRACT AND FULL-TEXT SCREENING — two independent screeners',
        'Open each URL through institutional access (e.g., the HEC National Digital Library). Read the abstract; if it may be eligible, read the full text.',
        'Screener 1 and Screener 2 work independently in separate copies of this file (save as screening_S1.xlsx and screening_S2.xlsx).',
        'Decision codes: INCLUDE, or EXCLUDE with reason E1-E4 (see criteria in manuscript Section 3.3), or FT-NA only if the full text truly cannot be obtained after trying institutional access and an author request.',
        'Record the access date. Disagreements are resolved afterwards by discussion or a third author; record the final decision in the "final" columns of screening_S1.xlsx.']:
        ws.append([line])
    ws.column_dimensions['A'].width = 140
    wsS = wb.create_sheet('Screening')
    head = ['record_id', 'source_database', 'title', 'year', 'url', 'abstract_decision', 'fulltext_decision', 'exclusion_code', 'access_date', 'note', 'final_decision', 'final_code']
    wsS.append(head)
    for c in wsS[1]: c.font = HDR
    for r in todo.itertuples():
        wsS.append([r.record_id, r.source_database, r.title, r.year, r.url] + [''] * 7)
    n = len(todo)
    for col, vals in [('F', '"INCLUDE_TO_FULLTEXT,EXCLUDE"'), ('G', '"INCLUDE,EXCLUDE,FT-NA,NOT_REACHED"'), ('H', '"E1,E2,E3,E4,FT-NA"'),
                      ('K', '"INCLUDE,EXCLUDE,FT-NA"'), ('L', '"E1,E2,E3,E4,FT-NA"')]:
        dv = DataValidation(type='list', formula1=vals, allow_blank=True); wsS.add_data_validation(dv); dv.add(f'{col}2:{col}{n + 1}')
    for col, w in zip('ABCDEFGHIJKL', [10, 14, 70, 7, 45, 20, 20, 12, 12, 30, 14, 12]): wsS.column_dimensions[col].width = w
    wsS.freeze_panes = 'C2'
    wb.save(OUT / '3_screening' / 'screening_template.xlsx')
    print('screening records:', n)
print('second-coder sample:', len(sample), sample)
