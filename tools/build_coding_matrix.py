"""Build the final source-level coding matrix from the reviewed C8 input.

The input is deliberately separate from the generated output so a rebuild cannot
silently restore the pre-C6 catalogue or discard audit traceability columns.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/literature_coding_matrix_authoritative.csv"
OUTPUT = ROOT / "data/literature_coding_matrix.csv"
REQUIRED = {
    "key", "short_cite", "year", "source_type", "evidence_basis", "research_stream",
    "modalities", "provenance", "context", "authority", "channel", "friction",
    "challenge", "feedback", "coding_justification", "reference", "audit_source_id",
    "version_mapping", "audit_decision", "evidence_urls", "traceability_note",
}


def read_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"No rows in {path}")
    missing = REQUIRED.difference(rows[0])
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    keys = [row["key"] for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate source keys in authoritative matrix")
    forbidden = {"ref51", "ref52", "ref94"}.intersection(keys)
    if forbidden:
        raise ValueError(f"C8-excluded keys present: {sorted(forbidden)}")
    return rows


def main():
    rows = read_rows(INPUT)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {OUTPUT} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
