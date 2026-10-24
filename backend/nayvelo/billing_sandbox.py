"""NAY-006 pure arithmetic on static fictional usage. Not a charging engine."""
from __future__ import annotations

import copy
import json
from datetime import date
from pathlib import Path

FIXTURE = Path(__file__).resolve().parents[2] / 'shared' / 'synthetic_billing.json'
FIELDS = {'schema_version', 'mode', 'source', 'currency', 'usage_unit',
          'forecast_days', 'sample_allowance_mib', 'sample_rate_kobo_per_gib',
          'days', 'illustrative_history', 'disclaimer'}
DAY_FIELDS = {'date', 'usage_mib'}
HISTORY_FIELDS = {'period', 'usage_mib', 'estimate_kobo'}


class UnsafeFixture(ValueError):
    """An unexpected fixture must fail closed rather than imply real billing."""


def _whole(value: object, minimum: int, maximum: int) -> bool:
    return type(value) is int and minimum <= value <= maximum


def estimate_kobo(usage_mib: int, rate_kobo_per_gib: int) -> int:
    """Rounded half-up once, in integer kobo; 1 GiB = 1024 MiB."""
    if not _whole(usage_mib, 0, 1_000_000) or not _whole(rate_kobo_per_gib, 1, 10_000_000):
        raise UnsafeFixture('Invalid fictional quantity or assumption')
    return (usage_mib * rate_kobo_per_gib + 512) // 1024


def forecast_mib(days: list[dict], horizon: int = 30) -> int:
    if not isinstance(days, list) or not 1 <= len(days) <= 31 or not _whole(horizon, 1, 31):
        raise UnsafeFixture('Unsupported forecast horizon')
    total = 0
    for day in days:
        if not isinstance(day, dict) or not _whole(day.get('usage_mib'), 0, 1_000_000):
            raise UnsafeFixture('Unsafe usage input')
        total += day['usage_mib']
    return (total * horizon + len(days) // 2) // len(days)


def validate_fixture(value: object) -> dict:
    if not isinstance(value, dict) or set(value) != FIELDS:
        raise UnsafeFixture('Unexpected synthetic fixture fields')
    required = {'schema_version': 1, 'mode': 'SIMULATION_ONLY',
                'source': 'FIXED_SYNTHETIC_FIXTURE', 'currency': 'NGN',
                'usage_unit': 'MiB', 'forecast_days': 30,
                'sample_allowance_mib': 8192,
                'sample_rate_kobo_per_gib': 125000}
    if any(type(value.get(k)) is not type(v) or value.get(k) != v for k, v in required.items()):
        raise UnsafeFixture('Fixture policy or assumptions changed')
    if not isinstance(value['disclaimer'], str) or 'Fictional usage' not in value['disclaimer']:
        raise UnsafeFixture('Fictional data disclaimer required')
    days = value['days']
    if not isinstance(days, list) or len(days) != 7:
        raise UnsafeFixture('Exactly seven synthetic daily examples required')
    seen = set()
    for idx, row in enumerate(days, 1):
        if not isinstance(row, dict) or set(row) != DAY_FIELDS or not _whole(row['usage_mib'], 0, 4096):
            raise UnsafeFixture('Unexpected daily event')
        try:
            d = date.fromisoformat(row['date'])
        except (ValueError, TypeError):
            raise UnsafeFixture('Malformed fictional date') from None
        if d.isoformat() != f'2026-10-{idx:02d}' or d in seen:
            raise UnsafeFixture('Unexpected or duplicate daily fixture dates')
        seen.add(d)
    history = value['illustrative_history']
    if not isinstance(history, list) or len(history) != 3:
        raise UnsafeFixture('Exactly three fictional past periods required')
    for idx, row in enumerate(history, 7):
        if not isinstance(row, dict) or set(row) != HISTORY_FIELDS:
            raise UnsafeFixture('Unexpected illustrative history fields')
        if row['period'] != f'2026-{idx:02d}' or not _whole(row['usage_mib'], 0, 100000):
            raise UnsafeFixture('Invalid fictional historical record')
        if type(row['estimate_kobo']) is not int or row['estimate_kobo'] != estimate_kobo(row['usage_mib'], 125000):
            raise UnsafeFixture('Illustrative estimate not reproducible')
    forecast_mib(days)
    return copy.deepcopy(value)


def get_fixture() -> dict:
    return validate_fixture(json.loads(FIXTURE.read_text(encoding='utf-8')))


def scenario(rate_ngn_per_gib: int = 1250, cap_ngn: int = 5000) -> dict:
    """Optional hypothetical rate/budget; never quotes commercial prices."""
    if not _whole(rate_ngn_per_gib, 500, 5000) or not _whole(cap_ngn, 1000, 50000):
        raise UnsafeFixture('Outside supported hypothetical rate or cap')
    fixture = get_fixture()
    projected_mib = forecast_mib(fixture['days'], fixture['forecast_days'])
    projected_kobo = estimate_kobo(projected_mib, rate_ngn_per_gib * 100)
    return {
        'simulated_usage_mib': sum(d['usage_mib'] for d in fixture['days']),
        'projected_30_day_mib': projected_mib,
        'projected_kobo': projected_kobo,
        'over_hypothetical_cap': projected_kobo > cap_ngn * 100,
        'simulated_allowance_mib': fixture['sample_allowance_mib'],
        'mode': 'SIMULATION_ONLY',
    }
