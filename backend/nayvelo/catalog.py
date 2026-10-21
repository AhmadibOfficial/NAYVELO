"""Concept catalog: not priced, purchasable or connected to a carrier."""
from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class Plan:
    code: str
    title: str
    period: str
    audience: str
    price_ngn: None = None
    available_for_purchase: bool = False
    description: str = 'Concept only — commercial terms not confirmed.'

PLANS = (
    Plan('daily-flex', 'Daily Flex', 'Daily', 'Occasional connectivity'),
    Plan('smart-weekly', 'Smart Weekly', 'Weekly', 'Flexible routines'),
    Plan('monthly-plus', 'Monthly Plus', 'Monthly', 'Everyday connectivity'),
    Plan('family-connect', 'Family Connect', 'Monthly', 'Families and shared households'),
    Plan('business-pro', 'Business Pro', 'Monthly', 'Business teams'),
    Plan('global-roam', 'Global Roam', 'Trip-based', 'International travelers'),
)

def get_plans() -> list[dict]:
    return [asdict(plan) for plan in PLANS]
