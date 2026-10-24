"""NAY-005: pure, nonpersistent demonstration domain. Never a subscriber API."""
from __future__ import annotations

import json
from pathlib import Path

POLICY_PATH = Path(__file__).resolve().parents[2] / 'shared' / 'demo_accounts.json'
_ALLOWED_ALIASES = frozenset({'DEMO-ALPHA', 'DEMO-BETA'})
_ALLOWED_STATES = frozenset({'preview', 'paused', 'locked', 'closed'})
_PRIVACY_KEYS = frozenset({'productAnalytics', 'productNews'})
_TRANSITIONS = {
    'preview': frozenset({'paused', 'locked', 'closed'}),
    'paused': frozenset({'preview', 'locked', 'closed'}),
    'locked': frozenset(),
    'closed': frozenset(),
}


class InvalidDemoAction(ValueError):
    """Reject unexpected data or unauthorized simulated state transitions."""


def policy() -> dict:
    """Load the static policy; never accept mutable identity or credential fields."""
    data = json.loads(POLICY_PATH.read_text(encoding='utf-8'))
    expected = {'schemaVersion', 'kind', 'simulationOnly', 'persistence', 'authentication',
                'personalDataCollected', 'optionalPrivacyDefaults', 'allowedStates',
                'allowedTransitions', 'profiles', 'disclaimer'}
    if set(data) != expected or data.get('schemaVersion') != 1 or data.get('kind') != 'NAYVELO_SIMULATED_ACCOUNT_POLICY':
        raise InvalidDemoAction('Unexpected schema field, version or policy kind')
    if data.get('simulationOnly') is not True or data.get('persistence') != 'memory_only':
        raise InvalidDemoAction('Simulation safety contract invalid')
    if data.get('authentication') != 'none' or data.get('personalDataCollected') is not False:
        raise InvalidDemoAction('Identity collection is not permitted')
    aliases = {row['alias'] for row in data.get('profiles', [])}
    if len(data.get('profiles', [])) != 2 or any(set(row) != {'alias', 'initialState'} or row['initialState'] not in _ALLOWED_STATES for row in data['profiles']):
        raise InvalidDemoAction('Invalid fictional profile shape')
    if aliases != _ALLOWED_ALIASES or set(data.get('allowedStates', [])) != _ALLOWED_STATES:
        raise InvalidDemoAction('Unrecognized demo profiles or states')
    if {k: frozenset(v) for k, v in data.get('allowedTransitions', {}).items()} != _TRANSITIONS:
        raise InvalidDemoAction('Unexpected account lifecycle policy')
    if data.get('optionalPrivacyDefaults') != {k: False for k in _PRIVACY_KEYS}:
        raise InvalidDemoAction('Privacy-default contract changed')
    return data


class DemoAccount:
    """Isolated memory-only fixture, not a customer object or identity record."""

    def __init__(self, alias: str):
        data = policy()
        entry = next((x for x in data['profiles'] if x['alias'] == alias), None)
        if entry is None:
            raise InvalidDemoAction('Only two fictional aliases are supported')
        self.alias = alias
        self.state = entry['initialState']
        self.privacy = dict(data['optionalPrivacyDefaults'])

    def transition(self, new_state: str) -> str:
        if not isinstance(new_state, str) or new_state not in _TRANSITIONS[self.state]:
            raise InvalidDemoAction('Transition blocked by demo policy')
        self.state = new_state
        return self.state

    def set_privacy(self, key: str, value: bool) -> None:
        if key not in _PRIVACY_KEYS or type(value) is not bool:
            raise InvalidDemoAction('Only local boolean privacy preferences allowed')
        self.privacy[key] = value

    def reset(self) -> None:
        self.__init__(self.alias)

    def public_view(self) -> dict:
        return {
            'alias': self.alias,
            'state': self.state,
            'privacy': dict(self.privacy),
            'simulationOnly': True,
            'saved': False,
        }
