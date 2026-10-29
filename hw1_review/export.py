"""Build a single-file, offline snapshot of the HW1 review UI and saved analysis."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from hw1_review import server


def build_export() -> str:
    payload = {
        'records': server.read_records(),
        'analysis_data': server.read_analysis(),
        'exported_at': datetime.now(timezone.utc).isoformat(),
    }
    # Escape HTML-significant characters so record text cannot close the data tag.
    data = json.dumps(payload, ensure_ascii=True).replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
    page = server.PAGE.read_text(encoding='utf-8')
    return page.replace('<!-- EXPORT_DATA -->', '<script type="application/json" id="embedded-data">' + data + '</script>')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=server.ROOT / 'reports' / 'cartwheel-hw1-review.html')
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build_export(), encoding='utf-8')
    print(f'Exported: {args.output.resolve()}')


if __name__ == '__main__':
    main()
