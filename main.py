"""Offline comparable-launch forecast; Python standard library only.

Quantiles use weighted nearest rank: the first sorted value whose cumulative
weight is at least tau * total weight. Smooth median and signed quantile
log-offsets separately with a centered three-hour mean (two at the edges).
"""
import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# The grader's -P leaves /bot off sys.path; allow sibling modules.
sys.path.insert(0, str(Path(__file__).resolve().parent))

LEVELS = [0.05, 0.25, 0.5, 0.75, 0.95]
Z = [-1.645, -0.674, 0, 0.674, 1.645]
SPREAD_FACTOR = 0.95
MEDIAN_SHRINKAGE = 1.0


def round2(x):
    """Match the starter's positive-number half-up rounding."""
    scaled = x * 100
    whole = math.floor(scaled)
    if scaled - whole >= 0.5:
        whole += 1
    value = whole / 100
    return int(value) if value.is_integer() else value


def finish(values):
    result = []
    for value in values:
        value = round2(min(1e9, max(0.01, value)))
        result.append(max(result[-1] if result else 0.01, value))
    return result


def utc_time(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    # Treat offset-free case timestamps as UTC, independent of the host timezone.
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def release_day_rows(comparable):
    """Return a complete, ordered UTC release-day slice, or an empty list."""
    if 'before release' in comparable.get('name', '').lower():
        return []
    date = utc_time(comparable['day_start']).date()
    rows = sorted((row for row in comparable['hourly']
                   if utc_time(row['from']).date() == date),
                  key=lambda row: utc_time(row['from']))
    if len(rows) != 24 or [utc_time(row['from']).hour for row in rows] != list(range(24)):
        return []
    return rows


def weighted_quantiles(samples):
    ordered = sorted(samples)
    total = math.fsum(weight for _, weight in ordered)
    result = []
    for tau in LEVELS:
        cumulative = 0.0
        selected = ordered[-1][0]
        for value, weight in ordered:
            cumulative += weight
            if cumulative >= tau * total:
                selected = value
                break
        result.append(selected)
    return result


def smooth(values):
    return [math.fsum(values[max(0, i-1):min(len(values), i+2)]) /
            len(values[max(0, i-1):min(len(values), i+2)])
            for i in range(len(values))]


def forecast_case(case, name='case'):
    if case['levels'] != LEVELS:
        raise ValueError(f'{name}: unexpected quantile levels')
    p1 = max(1, next(row['viewers'] for row in case['known'] if row['hour'] == 1))
    curves = []
    for comparable in case.get('comparables', []):
        rows = release_day_rows(comparable)
        if not rows or rows[0]['viewers'] < 5000:
            continue
        base = max(1, rows[0]['viewers'])
        weight = 0.05 + math.exp(-0.5 * (math.log(base) - math.log(p1)) ** 2)
        curves.append(([math.log(max(1, row['viewers']) / base) for row in rows[1:]], weight))
    if len(curves) < 5:
        return {'hours': [{'hour': row['hour'], 'q': finish([
            p1 * math.exp(z * 0.15 * math.sqrt(row['hour'] - 1)) for z in Z])}
            for row in case['forecast']]}
    raw = [weighted_quantiles([(curve[i], weight) for curve, weight in curves]) for i in range(23)]
    medians = smooth([q[2] for q in raw])
    offsets = [smooth([q[j] - q[2] for q in raw]) for j in range(5)]
    hours = []
    for row in case['forecast']:
        i = row['hour'] - 2
        values = [p1 * math.exp(MEDIAN_SHRINKAGE * medians[i] + SPREAD_FACTOR * offsets[j][i])
                  for j in range(5)]
        hours.append({'hour': row['hour'], 'q': finish(values)})
    return {'hours': hours}


def main():
    input_dir = Path(os.environ.get('MAKEFUN_INPUT_DIR', '/input'))
    output_dir = Path(os.environ.get('MAKEFUN_OUTPUT_DIR', '/output'))
    output_dir.mkdir(parents=True, exist_ok=True)
    for path in sorted(input_dir.glob('*.in')):
        case = json.loads(path.read_text(encoding='utf-8'))
        result = forecast_case(case, path.name)
        (output_dir / f'{path.stem}.out').write_text(
            json.dumps(result, separators=(',', ':'), allow_nan=False) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
