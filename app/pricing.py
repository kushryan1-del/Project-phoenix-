from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class PricingResult:
    material_tax: float
    total_direct_cost: float
    sell_price: float
    gross_profit: float
    gross_margin: float

    def as_dict(self) -> dict:
        return asdict(self)


def calculate_price(
    *,
    material_cost: float = 0,
    labor_cost: float = 0,
    subcontractor_cost: float = 0,
    permit_cost: float = 0,
    disposal_cost: float = 0,
    equipment_cost: float = 0,
    delivery_cost: float = 0,
    other_direct_cost: float = 0,
    material_tax_rate: float = 0.06,
    target_gross_margin: float = 0.30,
) -> PricingResult:
    """Project Phoenix pricing rule.

    Sales tax is applied to taxable material cost. All direct job costs are then
    divided by (1 - target gross margin). No separate material markup is used.
    """
    values = [
        material_cost,
        labor_cost,
        subcontractor_cost,
        permit_cost,
        disposal_cost,
        equipment_cost,
        delivery_cost,
        other_direct_cost,
    ]
    if any(v < 0 for v in values):
        raise ValueError("Direct costs cannot be negative.")
    if not 0 <= material_tax_rate < 1:
        raise ValueError("Material tax rate must be between 0 and 1.")
    if not 0 <= target_gross_margin < 1:
        raise ValueError("Target gross margin must be between 0 and 1.")

    material_tax = material_cost * material_tax_rate
    total_direct_cost = sum(values) + material_tax
    sell_price = total_direct_cost / (1 - target_gross_margin) if total_direct_cost else 0
    gross_profit = sell_price - total_direct_cost
    gross_margin = gross_profit / sell_price if sell_price else 0

    return PricingResult(
        material_tax=round(material_tax, 2),
        total_direct_cost=round(total_direct_cost, 2),
        sell_price=round(sell_price, 2),
        gross_profit=round(gross_profit, 2),
        gross_margin=round(gross_margin, 6),
    )
