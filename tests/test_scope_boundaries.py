from pathlib import Path

import thalmetis_edr

ROOT = Path(__file__).resolve().parents[1]

PROHIBITED_PUBLIC_NAMES = {
    "predict_viability",
    "optimize_sparger",
    "validate_bioreactor",
    "estimate_rupture_viability",
    "rupture_viability",
    "predict_rupture_viability",
    "estimate_combined_viability",
    "pinch_off_plus_rupture_viability",
    "estimate_event_history_viability",
    "coalescence_viability",
    "path_independence_viability",
}

PROHIBITED_DEPENDENCIES = {
    "streamlit",
    "dash",
    "gradio",
    "flask",
    "fastapi",
    "django",
    "panel",
    "bokeh",
    "plotly",
    "uvicorn",
    "gunicorn",
    "xgboost",
}


def test_no_prohibited_public_api_names_are_exported() -> None:
    exported = set(thalmetis_edr.__all__)

    assert exported.isdisjoint(PROHIBITED_PUBLIC_NAMES)
    for name in PROHIBITED_PUBLIC_NAMES:
        assert not hasattr(thalmetis_edr, name)


def test_no_prohibited_ui_or_web_dependencies() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8").lower()

    for dependency in PROHIBITED_DEPENDENCIES:
        assert f'"{dependency}' not in pyproject
        assert f"'{dependency}" not in pyproject


def test_readme_and_docs_contain_required_boundaries() -> None:
    combined_text = "\n".join(
        [
            (ROOT / "README.md").read_text(encoding="utf-8"),
            (ROOT / "docs" / "model-boundaries.md").read_text(encoding="utf-8"),
            (ROOT / "docs" / "future-event-history.md").read_text(
                encoding="utf-8"
            ),
        ]
    )

    required_phrases = [
        "first-class v0.1 packaged viability model is McRae et al. 2024 "
        "pinch-off / Table 3 only",
        "Walls et al. 2017 affected-volume-only",
        "no rupture viability model",
        "no combined pinch-off + rupture viability model",
        "user-composed exploratory calculation",
    ]

    for phrase in required_phrases:
        assert phrase in combined_text


def test_citation_has_no_doi_until_real_zenodo_release() -> None:
    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")

    assert "title: thalmetis-edr" in citation
    assert "given-names: Oliver" in citation
    assert "version: 0.1.0" in citation
    assert "doi:" not in citation.lower()
    assert "Zenodo DOI will be added after the first GitHub release" in citation
