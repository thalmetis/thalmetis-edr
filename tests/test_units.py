import pytest

from thalmetis_edr.units import liters_to_m3, ml_to_m3, mm_to_m, nl_to_m3


def test_unit_conversions_match_expected_si_values() -> None:
    assert nl_to_m3(1.0) == pytest.approx(1.0e-12)
    assert liters_to_m3(5000.0) == pytest.approx(5.0)
    assert liters_to_m3(1_152_000.0) == pytest.approx(1152.0)
    assert mm_to_m(0.18) == pytest.approx(1.8e-4)
    assert ml_to_m3(2.5) == pytest.approx(2.5e-6)
