"""NAY-008 interface-only carrier boundary, never a carrier connector.

No network client, credentials, provisioning payloads, or runtime enable switch.
The only adapter is a fail-closed demonstrator. All examples are fictional.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
from typing import NoReturn, Protocol

FIXTURE = Path(__file__).resolve().parents[2] / 'shared' / 'carrier_readiness.json'

BOUNDARIES = (
    'network_access', 'esim_provisioning', 'service_management',
    'usage_reporting', 'subscriber_registration',
)
GATES = (
    'ncc_licensing', 'wholesale_contract', 'rsp_partner',
    'subscriber_compliance', 'security_assurance', 'interoperability',
    'service_operations', 'commercial_assurance',
)


class ContractRejected(ValueError):
    """Invalid public demonstrator schema. Never surface raw data in errors."""


class CarrierOperationDenied(PermissionError):
    """A future telecom command was attempted in simulation mode."""


class CarrierAction(str, Enum):
    PROVISION_PROFILE = 'PROVISION_PROFILE'
    CHANGE_SERVICE_STATE = 'CHANGE_SERVICE_STATE'
    QUERY_NETWORK_USAGE = 'QUERY_NETWORK_USAGE'
    ASSIGN_NUMBER = 'ASSIGN_NUMBER'
    REGISTER_SUBSCRIBER = 'REGISTER_SUBSCRIBER'


@dataclass(frozen=True, slots=True)
class FictionalCommand:
    """Architectural command shape only: no EID/ICCID/IMSI/NIN/MSISDN or URLs."""
    action: CarrierAction
    scenario: str = 'EXAMPLE_ONLY'

    def __post_init__(self) -> None:
        if type(self.action) is not CarrierAction or self.scenario != 'EXAMPLE_ONLY':
            raise ContractRejected('Only fictional interface commands allowed')


class FutureCarrierPort(Protocol):
    """Contract shape for a SEPARATE, legally approved future implementation."""
    def describe(self) -> dict: ...
    def execute(self, command: FictionalCommand) -> NoReturn: ...


def validate_readiness(value: object) -> dict:
    """Schema-validate a strictly fixed public fixture, rejecting injected identifiers."""
    if type(value) is not dict:
        raise ContractRejected('Fixture is not an object')
    root = {'schema_version','mode','source','integration_state','network_connected',
            'esim_provisioning_enabled','real_subscribers_enabled','payments_enabled',
            'description','boundaries','certification_gates','disclaimer'}
    if set(value) != root:
        raise ContractRejected('Unexpected public fixture field')
    exact = {
        'schema_version': 1,
        'mode': 'SIMULATION_ONLY',
        'source': 'PUBLIC_FIXED_INTERFACE_DESIGN',
        'integration_state': 'NOT_AUTHORIZED',
        'network_connected': False,
        'esim_provisioning_enabled': False,
        'real_subscribers_enabled': False,
        'payments_enabled': False,
    }
    if any(type(value[key]) is not type(expected) or value[key] != expected
           for key, expected in exact.items()):
        raise ContractRejected('Live service or altered mode is prohibited')
    if type(value['description']) is not str or not value['description'].startswith('Architecture exercise only.'):
        raise ContractRejected('Missing design-only warning')
    if value['disclaimer'] != ('PUBLIC DESIGN DEMONSTRATION ONLY. This dashboard is not certification, regulator approval, a network connection, a subscriber account, live telemetry or a carrier-provisioning tool.'):
        raise ContractRejected('Required public warning changed')
    boundaries = value['boundaries']
    if type(boundaries) is not list or len(boundaries) != len(BOUNDARIES):
        raise ContractRejected('Wrong boundary count')
    boundary_labels = (
        'Host-network interfaces','eSIM profile provisioning',
        'Voice, SMS and service-state operations','Network usage and billing feeds',
        'Subscriber identity and registration',
    )
    for index, (item, code, label) in enumerate(zip(boundaries, BOUNDARIES, boundary_labels)):
        if type(item) is not dict or set(item) != {'code','label','state','detail'}:
            raise ContractRejected('Unexpected boundary data')
        if item['code'] != code or item['label'] != label or item['state'] != 'BLOCKED':
            raise ContractRejected('Boundary must remain blocked')
        if type(item['detail']) is not str or not (10 <= len(item['detail']) <= 130):
            raise ContractRejected('Invalid boundary explanation')
        if any(x in item['detail'].lower() for x in ('http://','https://','api_key','token=','@')):
            raise ContractRejected('No network addresses or identifiers')
    gates = value['certification_gates']
    if type(gates) is not list or len(gates) != len(GATES):
        raise ContractRejected('Unexpected certification evidence')
    labels = (
        'NCC authorization / permitted operating model',
        'Executed host-network commercial and technical contract',
        'Authorized eSIM provisioning and GSMA applicability review',
        'Subscriber registration and data-protection review',
        'Threat modeling, independent testing and key management',
        'Partner test environment and interoperability evidence',
        'Support, incident, fraud and abuse handling',
        'Tariffs, disclosures, dispute and usage reconciliation',
    )
    for item, code, label in zip(gates, GATES, labels):
        if type(item) is not dict or set(item) != {'code','label','status'}:
            raise ContractRejected('Unexpected gate data')
        if item != {'code':code,'label':label,'status':'NOT_VERIFIED'}:
            raise ContractRejected('Missing evidence cannot be declared verified')
    # JSON round-trip guarantees isolation; callers cannot mutate a shared state.
    return json.loads(json.dumps(value))


def public_readiness() -> dict:
    return validate_readiness(json.loads(FIXTURE.read_text(encoding='utf-8')))


class BlockedCarrierAdapter:
    """Only permissible local implementation of FutureCarrierPort."""

    def describe(self) -> dict:
        return public_readiness()

    def execute(self, command: FictionalCommand) -> NoReturn:
        # Deny before any command decoding, network access, or side effects.
        raise CarrierOperationDenied('SIMULATION_ONLY: carrier operations are not authorized')
