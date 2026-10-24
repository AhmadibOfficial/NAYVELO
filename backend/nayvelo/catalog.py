"""Fail-closed concept catalog backed by shared/plans.json. Never represents an offer."""
from __future__ import annotations

import copy
import json
from pathlib import Path

CATALOG = Path(__file__).resolve().parents[2] / 'shared' / 'plans.json'
REQUIRED_FIELDS = frozenset({
    'code', 'title', 'period', 'audience', 'description',
    'data_gb', 'voice_minutes', 'sms_count', 'price_ngn',
    'hotspot', 'rollover', 'available_for_purchase',
})
UNKNOWN_ALLOWANCES = ('data_gb', 'voice_minutes', 'sms_count', 'price_ngn')


def validate_catalog_data(value: object) -> list[dict]:
    if not isinstance(value, dict) or value.get('mode') != 'SIMULATION_ONLY' or value.get('schema_version') != 1:
        raise ValueError('Catalog must be a versioned SIMULATION_ONLY fixture')
    if not isinstance(value.get('disclaimer'), str) or not value['disclaimer'].strip():
        raise ValueError('Catalog disclaimer is required')
    plans = value.get('plans')
    if not isinstance(plans, list) or not plans:
        raise ValueError('At least one concept plan is required')
    codes: set[str] = set()
    for p in plans:
        if not isinstance(p, dict) or set(p) != REQUIRED_FIELDS:
            raise ValueError('Unexpected or missing plan fields')
        if any(p[field] is not None for field in UNKNOWN_ALLOWANCES):
            raise ValueError('Prices and allowances are not confirmed; use null')
        if p['available_for_purchase'] is not False:
            raise ValueError('No concept plan is purchasable')
        for field in ('code', 'title', 'period', 'audience', 'description'):
            if not isinstance(p[field], str) or not p[field].strip():
                raise ValueError(f'Invalid plan {field}')
        if not all(p[k] == 'Not confirmed' for k in ('hotspot', 'rollover')):
            raise ValueError('Hotspot and rollover are not confirmed')
        if p['code'] in codes:
            raise ValueError('Duplicate plan code')
        codes.add(p['code'])
    return copy.deepcopy(plans)


def get_plans() -> list[dict]:
    """Return a new validated value per read, never mutable shared state."""
    return validate_catalog_data(json.loads(CATALOG.read_text(encoding='utf-8')))
