"""Strictly validated, immutable synthetic NAY-007 admin analytics: NOT an admin API."""
from __future__ import annotations

import copy
import json
from pathlib import Path

FIXTURE = Path(__file__).resolve().parents[2] / 'shared' / 'synthetic_admin.json'
ROOT_KEYS = {'schema_version', 'mode', 'source', 'period', 'plan_concepts', 'weeks',
             'plan_interest', 'demo_operations', 'disclaimer'}
WEEK_KEYS = {'label', 'visits', 'onboarding_previews', 'help_requests'}
PLAN_KEYS = {'code', 'count'}
OP_KEYS = {'code', 'label', 'state'}
CODES = ('daily-flex','smart-weekly','monthly-plus','family-connect','business-pro','global-roam')
OPCODES = ('documentation','support','partnership')
ROLES = ('viewer','analyst','operator')

class InvalidSyntheticAnalytics(ValueError):
    pass

def integer(value: object, lo: int, hi: int) -> bool:
    return type(value) is int and lo <= value <= hi

def validate_fixture(value: object) -> dict:
    if not isinstance(value, dict) or set(value) != ROOT_KEYS:
        raise InvalidSyntheticAnalytics('Unknown fixture fields (including identity fields)')
    constants = {'schema_version': 1, 'mode': 'SIMULATION_ONLY',
                 'source': 'PUBLIC_FIXED_FICTIONAL_DATA', 'plan_concepts': 6,
                 'period': 'Four invented example weeks; not current activity'}
    if any(type(value.get(k)) is not type(v) or value.get(k) != v for k,v in constants.items()):
        raise InvalidSyntheticAnalytics('Synthetic-only policy violated')
    if not isinstance(value['disclaimer'],str) or not value['disclaimer'].startswith('Fictional administrative exercise only.') or 'NOT authentication' not in value['disclaimer']:
        raise InvalidSyntheticAnalytics('Required warning missing')
    weeks=value['weeks']
    if not isinstance(weeks,list) or len(weeks)!=4:
        raise InvalidSyntheticAnalytics('Exactly four fictional weeks required')
    for i,w in enumerate(weeks,1):
        if not isinstance(w,dict) or set(w)!=WEEK_KEYS or w['label']!=f'Example week {i}':
            raise InvalidSyntheticAnalytics('Unexpected week fields')
        if any(not integer(w[k],0,10000) for k in ('visits','onboarding_previews','help_requests')):
            raise InvalidSyntheticAnalytics('Unsafe aggregate counts')
        if w['onboarding_previews']>w['visits'] or w['help_requests']>w['visits']:
            raise InvalidSyntheticAnalytics('Inconsistent synthetic counts')
    plans=value['plan_interest']
    if not isinstance(plans,list) or len(plans)!=6:
        raise InvalidSyntheticAnalytics('Six concept plan counts required')
    for i,p in enumerate(plans):
        if not isinstance(p,dict) or set(p)!=PLAN_KEYS or p['code']!=CODES[i] or not integer(p['count'],0,10000):
            raise InvalidSyntheticAnalytics('Unknown plan interest or count')
    operations=value['demo_operations']
    if not isinstance(operations,list) or len(operations)!=3:
        raise InvalidSyntheticAnalytics('Only three mock operational checks')
    for i,op in enumerate(operations):
        if not isinstance(op,dict) or set(op)!=OP_KEYS or op['code']!=OPCODES[i]:
            raise InvalidSyntheticAnalytics('Unexpected operation or identity data')
        if not isinstance(op['label'],str) or op['label'] not in ('Readiness guide review','Simulated support queue','Carrier integration prerequisite'):
            raise InvalidSyntheticAnalytics('Unexpected operation label')
        if op['state'] != ('not_authorized' if i==2 else 'illustrative_only'):
            raise InvalidSyntheticAnalytics('Operational state must fail closed')
    return copy.deepcopy(value)

def load_fixture() -> dict:
    return validate_fixture(json.loads(FIXTURE.read_text(encoding='utf-8')))

def role_view(role: str, source: dict | None = None) -> dict:
    """Illustrates least privilege; NOT a real authority check or access token."""
    if type(role) is not str or role not in ROLES:
        raise InvalidSyntheticAnalytics('Unknown fictional role; default deny')
    fixture=validate_fixture(source if source is not None else load_fixture())
    weeks=fixture['weeks']
    result={'role':role,'mode':'SIMULATION_ONLY','role_simulated':True,
            'summary': {'fictional_visits':sum(w['visits'] for w in weeks),
                        'fictional_previews':sum(w['onboarding_previews'] for w in weeks),
                        'plan_concepts':fixture['plan_concepts']}}
    if role in ('analyst','operator'):
        result['weekly_trends']=copy.deepcopy(weeks)
        result['plan_interest']=copy.deepcopy(fixture['plan_interest'])
    if role=='operator':
        result['demo_operations']=copy.deepcopy(fixture['demo_operations'])
    return result
