"""NAY-009: fully offline, fictional partner-response contract conformance laboratory.

Not an MVNO integration, eSIM stack, API client, account system, or network simulator.
All examples are static/read-only; no socket, URL, credentials, subscriber identity,
clock, random data, storage, telemetry, or external service dependencies.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

FIXTURE = Path(__file__).resolve().parents[2] / 'shared' / 'partner_lab.json'
REQUEST_TAG = 'NAY-009-FIXTURE'
DEADLINE_MS = 500

SCENARIOS = (
    ('nominal_ack', 'Valid fictional acknowledgment', 'NONE', 'ACCEPTED'),
    ('timeout', 'Response timeout', 'TIMEOUT', 'REJECTED_TIMEOUT'),
    ('duplicate_response', 'Duplicate delivery', 'DUPLICATE', 'REJECTED_DUPLICATE'),
    ('out_of_order', 'Out-of-order sequence', 'OUT_OF_ORDER', 'REJECTED_SEQUENCE'),
    ('mismatched_tag', 'Correlation mismatch', 'MISMATCHED_TAG', 'REJECTED_CORRELATION'),
    ('schema_drift', 'Unexpected response property', 'SCHEMA_DRIFT', 'REJECTED_SCHEMA'),
    ('partner_error', 'Partner says unavailable', 'PARTNER_ERROR', 'REJECTED_PARTNER_ERROR'),
    ('pii_injection', 'Injected identity property', 'PII_INJECTION', 'REJECTED_SCHEMA'),
    ('empty_response', 'Missing acknowledgment', 'EMPTY', 'REJECTED_NO_RESPONSE'),
)
DISCLAIMER = ('EDUCATIONAL OFFLINE CONTRACT LAB ONLY. All responses are fictional; '
              'no carrier, eSIM provisioning, payment, identity or external partner '
              'is connected or certified.')


class LabContractViolation(ValueError):
    """A response or fixture was rejected without leaking its content."""


@dataclass(frozen=True, slots=True)
class LabVerdict:
    outcome: str
    accepted: bool


def validate_fixture(value: object) -> dict:
    if type(value) is not dict or set(value) != {
        'schema_version', 'mode', 'source', 'network_connected',
        'activation_enabled', 'payments_enabled', 'real_subscribers_enabled',
        'certification_status', 'disclaimer', 'scenarios'
    }:
        raise LabContractViolation('Unexpected partner laboratory fixture')
    expected = {
        'schema_version': 1, 'mode': 'SIMULATION_ONLY',
        'source': 'FIXED_SYNTHETIC_PARTNER_LAB', 'network_connected': False,
        'activation_enabled': False, 'payments_enabled': False,
        'real_subscribers_enabled': False, 'certification_status': 'NOT_VERIFIED',
        'disclaimer': DISCLAIMER,
    }
    if any(type(value[k]) is not type(v) or value[k] != v for k, v in expected.items()):
        raise LabContractViolation('Unsafe laboratory state or false certification claim')
    scenarios = value['scenarios']
    if type(scenarios) is not list or len(scenarios) != len(SCENARIOS):
        raise LabContractViolation('Unexpected scenario count')
    for item, (code, label, fault, result) in zip(scenarios, SCENARIOS):
        if type(item) is not dict or set(item) != {
            'code', 'label', 'fault', 'expected', 'explanation'
        } or any(type(item[k]) is not str for k in item):
            raise LabContractViolation('Unsafe scenario shape')
        if (item['code'], item['label'], item['fault'], item['expected']) != (
                code, label, fault, result):
            raise LabContractViolation('Scenario facts or safe expected outcome changed')
        explanation = item['explanation']
        if not 30 <= len(explanation) <= 180 or any(
            term in explanation.lower() for term in ('http:', 'https:', 'token=', '@', 'nin=', 'iccid=', 'eid=')
        ):
            raise LabContractViolation('Unsafe scenario explanation')
    return json.loads(json.dumps(value))


def load_fixture() -> dict:
    return validate_fixture(json.loads(FIXTURE.read_text(encoding='utf-8')))


def _example_response(*, sequence: int = 1, result: str = 'ACK',
                      request_tag: str = REQUEST_TAG, latency_ms: int = 10) -> dict:
    return {'request_tag': request_tag, 'sequence': sequence,
            'operation': 'READINESS_ONLY', 'result': result,
            'latency_ms': latency_ms, 'simulation_only': True}


def inspect_replies(responses: object) -> LabVerdict:
    """Read-only strict response parser; no retry, mutation, network or provisioning."""
    if type(responses) is not list:
        return LabVerdict('REJECTED_SCHEMA', False)
    if not responses:
        return LabVerdict('REJECTED_NO_RESPONSE', False)
    if len(responses) != 1:
        return LabVerdict('REJECTED_DUPLICATE', False)
    item = responses[0]
    if type(item) is not dict or set(item) != {
        'request_tag', 'sequence', 'operation', 'result', 'latency_ms', 'simulation_only'
    }:
        return LabVerdict('REJECTED_SCHEMA', False)
    if (type(item['request_tag']) is not str or
        type(item['sequence']) is not int or
        type(item['operation']) is not str or
        type(item['result']) is not str or
        type(item['latency_ms']) is not int or
        type(item['simulation_only']) is not bool):
        return LabVerdict('REJECTED_SCHEMA', False)
    if item['simulation_only'] is not True or item['operation'] != 'READINESS_ONLY':
        return LabVerdict('REJECTED_SCHEMA', False)
    if item['request_tag'] != REQUEST_TAG:
        return LabVerdict('REJECTED_CORRELATION', False)
    if item['sequence'] != 1:
        return LabVerdict('REJECTED_SEQUENCE', False)
    if item['latency_ms'] < 0 or item['latency_ms'] > DEADLINE_MS:
        return LabVerdict('REJECTED_TIMEOUT', False)
    if item['result'] != 'ACK':
        return LabVerdict('REJECTED_PARTNER_ERROR', False)
    return LabVerdict('ACCEPTED', True)


def replay_scenario(code: str) -> LabVerdict:
    """Generate a response in memory and validate it; never send a request."""
    cases = {row[0]: row for row in SCENARIOS}
    if type(code) is not str or code not in cases:
        raise LabContractViolation('Unknown fictional scenario')
    fault = cases[code][2]
    event = _example_response()
    if fault == 'NONE':
        replies = [event]
    elif fault == 'TIMEOUT':
        replies = [{**event, 'latency_ms': DEADLINE_MS + 1}]
    elif fault == 'DUPLICATE':
        replies = [event, event.copy()]
    elif fault == 'OUT_OF_ORDER':
        replies = [{**event, 'sequence': 2}]
    elif fault == 'MISMATCHED_TAG':
        replies = [{**event, 'request_tag': 'NAY-009-OTHER'}]
    elif fault == 'SCHEMA_DRIFT':
        replies = [{**event, 'network_url': 'EXAMPLE_INVALID_FIELD'}]
    elif fault == 'PARTNER_ERROR':
        replies = [{**event, 'result': 'TEMPORARY_UNAVAILABLE'}]
    elif fault == 'PII_INJECTION':
        replies = [{**event, 'nin': 'BLOCKED_EXAMPLE_FIELD'}]
    else:  # EMPTY
        replies = []
    return inspect_replies(replies)


def public_report() -> dict:
    fixture = load_fixture()
    results = []
    for row in fixture['scenarios']:
        outcome = replay_scenario(row['code'])
        if outcome.outcome != row['expected']:
            raise LabContractViolation('Synthetic conformance outcome diverged')
        results.append({
            'code': row['code'], 'label': row['label'],
            'explanation': row['explanation'], 'outcome': outcome.outcome,
            'accepted': outcome.accepted,
        })
    return {
        'schema_version': 1, 'mode': 'SIMULATION_ONLY',
        'integration_state': 'NOT_AUTHORIZED',
        'network_connected': False, 'payments_enabled': False,
        'real_subscribers_enabled': False, 'activation_enabled': False,
        'certification_status': 'NOT_VERIFIED', 'disclaimer': DISCLAIMER,
        'scenario_count': len(results), 'scenarios': results,
        'verdict_meaning': 'ACCEPTED describes a fixed fictional response only; never partner certification.',
    }
