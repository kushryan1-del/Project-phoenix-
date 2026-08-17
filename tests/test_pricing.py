from app.pricing import calculate_price


def test_standard_30_percent_margin():
    result = calculate_price(material_cost=1000, labor_cost=1000, material_tax_rate=.06, target_gross_margin=.30)
    assert result.material_tax == 60.00
    assert result.total_direct_cost == 2060.00
    assert result.sell_price == 2942.86
    assert round(result.gross_margin, 2) == .30


def test_no_material_markup_is_added():
    result = calculate_price(material_cost=100, material_tax_rate=.06, target_gross_margin=.30)
    assert result.total_direct_cost == 106.00
    assert result.sell_price == 151.43


def test_high_risk_margin():
    result = calculate_price(labor_cost=600, disposal_cost=100, target_gross_margin=.40)
    assert result.total_direct_cost == 700.00
    assert result.sell_price == 1166.67
