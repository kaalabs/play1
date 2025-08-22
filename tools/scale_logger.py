"""Scale/tank JSON-lines to CSV logger.

Reads JSON objects from stdin (one per line) and writes a CSV to a file.
Reusable function `rows_to_csv(rows)` returns CSV as a string for tests.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from typing import Iterable, Dict, Any


COLUMNS = [
    'timestamp',
    'source',
    'weight_g',
    'flow_gps',
    'stable',
    'level_pct',
    'tank_state',
]


def _coerce(v, t=float, default=None):
    try:
        return t(v)
    except Exception:
        return default


def rows_to_csv(rows: Iterable[Dict[str, Any]]) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLUMNS)
    w.writeheader()
    for r in rows:
        # Accept either scale-only or aggregate objects
        if 'tank' in r or 'scale' in r:
            tank = r.get('tank') or {}
            scale = r.get('scale') or {}
            row = {
                'timestamp': r.get('ts') or r.get('timestamp'),
                'source': scale.get('source'),
                'weight_g': scale.get('weight_g'),
                'flow_gps': scale.get('flow_gps'),
                'stable': scale.get('stable'),
                'level_pct': tank.get('level_pct'),
                'tank_state': tank.get('state'),
            }
        else:
            row = {
                'timestamp': r.get('ts') or r.get('timestamp'),
                'source': r.get('source'),
                'weight_g': r.get('weight_g'),
                'flow_gps': r.get('flow_gps'),
                'stable': r.get('stable'),
                'level_pct': r.get('level_pct'),
                'tank_state': r.get('state') or r.get('tank_state'),
            }
        w.writerow(row)
    return buf.getvalue()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument('-o', '--output', required=True, help='Output CSV path')
    args = p.parse_args(argv)

    rows = []
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            rows.append(obj)
        except json.JSONDecodeError:
            continue
    csv_text = rows_to_csv(rows)
    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        f.write(csv_text)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
