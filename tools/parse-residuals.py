#!/usr/bin/env python3
"""
Parse OpenFOAM solver log and extract residuals for convergence analysis.

Usage:
    python3 tools/parse-residuals.py log.simpleFoam
    python3 tools/parse-residuals.py log.simpleFoam --plot
    python3 tools/parse-residuals.py log.simpleFoam --csv > residuals.csv
    python3 tools/parse-residuals.py log.simpleFoam --json
"""

import argparse
import csv
import io
import json
import re
import sys
from pathlib import Path


RESIDUAL_PATTERN = re.compile(
    r'Solving for (\w+),.*Initial residual = ([\d.eE+-]+),.*Final residual = ([\d.eE+-]+)'
)
TIME_PATTERN = re.compile(r'^Time = ([\d.eE+-]+)')
COURANT_PATTERN = re.compile(r'Courant Number mean: ([\d.eE+-]+) max: ([\d.eE+-]+)')
CONTINUITY_PATTERN = re.compile(r'time step continuity errors.*sum local = ([\d.eE+-]+)')


def parse_log(log_path: str) -> list[dict]:
    """Parse an OpenFOAM log file into structured data."""
    records = []
    current_time = 0.0
    current_record = {}

    with open(log_path) as f:
        for line in f:
            # Time step
            m = TIME_PATTERN.match(line)
            if m:
                if current_record:
                    records.append(current_record)
                current_time = float(m.group(1))
                current_record = {'time': current_time}
                continue

            # Residuals
            m = RESIDUAL_PATTERN.search(line)
            if m:
                field = m.group(1)
                current_record[f'{field}_initial'] = float(m.group(2))
                current_record[f'{field}_final'] = float(m.group(3))
                continue

            # Courant
            m = COURANT_PATTERN.search(line)
            if m:
                current_record['Co_mean'] = float(m.group(1))
                current_record['Co_max'] = float(m.group(2))
                continue

            # Continuity
            m = CONTINUITY_PATTERN.search(line)
            if m:
                current_record['continuity'] = float(m.group(1))

    if current_record:
        records.append(current_record)

    return records


def output_csv(records: list[dict], stream=sys.stdout):
    """Write records as CSV."""
    if not records:
        return
    fields = list(records[0].keys())
    for r in records[1:]:
        for k in r:
            if k not in fields:
                fields.append(k)

    writer = csv.DictWriter(stream, fieldnames=fields)
    writer.writeheader()
    writer.writerows(records)


def output_json(records: list[dict]):
    """Write records as JSON."""
    print(json.dumps(records, indent=2))


def output_summary(records: list[dict]):
    """Print convergence summary."""
    if not records:
        print("No data found in log.")
        return

    last = records[-1]
    print(f"Time steps: {len(records)}")
    print(f"Final time: {last.get('time', 'N/A')}")
    print(f"Courant: mean={last.get('Co_mean', 'N/A')}, max={last.get('Co_max', 'N/A')}")
    print(f"Continuity: {last.get('continuity', 'N/A')}")
    print()

    # Find residual fields
    residual_fields = [k.replace('_final', '') for k in last if k.endswith('_final')]
    print("Final residuals:")
    for field in residual_fields:
        val = last.get(f'{field}_final', 'N/A')
        status = '✓' if isinstance(val, float) and val < 1e-5 else '✗'
        print(f"  {status} {field}: {val}")


def main():
    parser = argparse.ArgumentParser(description='Parse OpenFOAM residuals')
    parser.add_argument('log_file', help='Path to solver log file')
    parser.add_argument('--csv', action='store_true', help='Output as CSV')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--plot', action='store_true', help='Generate convergence plot')
    args = parser.parse_args()

    records = parse_log(args.log_file)

    if args.csv:
        output_csv(records)
    elif args.json:
        output_json(records)
    elif args.plot:
        try:
            import matplotlib.pyplot as plt
            import numpy as np

            times = [r['time'] for r in records]
            fields = [k.replace('_final', '') for k in records[0] if k.endswith('_final')]

            fig, ax = plt.subplots(figsize=(10, 6))
            for field in fields:
                vals = [r.get(f'{field}_final', float('nan')) for r in records]
                ax.semilogy(times, vals, label=field)

            ax.set_xlabel('Time (s)')
            ax.set_ylabel('Residual')
            ax.set_title('Convergence History')
            ax.legend()
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig('convergence.pdf', dpi=300)
            print("Saved: convergence.pdf")
        except ImportError:
            print("matplotlib required for plotting: pip install matplotlib", file=sys.stderr)
            sys.exit(1)
    else:
        output_summary(records)


if __name__ == '__main__':
    main()
