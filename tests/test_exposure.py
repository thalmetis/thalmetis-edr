import pytest

from thalmetis_edr.exposure import EventContribution, ExposureHistory, ThresholdExposure


def test_exposure_metadata_containers_are_importable() -> None:
    threshold = ThresholdExposure(event_kind="pinch_off")
    contribution = EventContribution(event_kind="future_experimental")
    history = ExposureHistory(contributions=[contribution])

    assert threshold.event_kind == "pinch_off"
    assert history.contributions == [contribution]


def test_exposure_history_does_not_implement_viability_behavior() -> None:
    history = ExposureHistory()

    with pytest.raises(NotImplementedError):
        history.estimate_viability()
