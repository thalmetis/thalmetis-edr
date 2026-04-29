"""Unit labels and conversion helpers used by structured result objects."""

VOLUME_M3 = "m^3"
LENGTH_M = "m"
ENERGY_DISSIPATION_RATE_W_M3 = "W/m^3"
VIABILITY_FRACTION = "fraction"
VIABILITY_PERCENT = "percent"
EVENT_COUNT = "count"


def nl_to_m3(value_nl: float) -> float:
    """Convert nanoliters to cubic meters."""
    return value_nl * 1.0e-12


def ml_to_m3(value_ml: float) -> float:
    """Convert milliliters to cubic meters."""
    return value_ml * 1.0e-6


def liters_to_m3(value_liters: float) -> float:
    """Convert liters to cubic meters."""
    return value_liters * 1.0e-3


def mm_to_m(value_mm: float) -> float:
    """Convert millimeters to meters."""
    return value_mm * 1.0e-3


def um_to_m(value_um: float) -> float:
    """Convert micrometers to meters."""
    return value_um * 1.0e-6


def percent_to_fraction(value_percent: float) -> float:
    """Convert percent to fraction."""
    return value_percent / 100.0
