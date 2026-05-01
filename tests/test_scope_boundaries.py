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
    combined_text = " ".join(
        "\n".join(
            [
                (ROOT / "README.md").read_text(encoding="utf-8"),
                (ROOT / "docs" / "model-boundaries.md").read_text(encoding="utf-8"),
                (ROOT / "docs" / "future-event-history.md").read_text(encoding="utf-8"),
                (ROOT / "docs" / "pinchoff-viability-estimate.md").read_text(
                    encoding="utf-8"
                ),
                (ROOT / "docs" / "v0.2-release-readiness.md").read_text(
                    encoding="utf-8"
                ),
            ]
        ).split()
    )

    required_phrases = [
        "v0.1 reconstructed the bounded McRae 2024 Figure 5a/Table 3 pathway",
        "v0.2 adds bounded interpolation and user-defined pinch-off "
        "sensitivity estimates",
        "Walls et al. 2017 affected-volume-only",
        "bounded sensitivity estimate",
        "not a validated industrial viability predictor",
        "not the main commercial Thalmetis transfer-readiness product",
        "process control, GMP release, transfer approval, process approval, "
        "or batch release",
        "Users supply EDR threshold and single-event viability-loss assumptions",
        "inferred Table 3 `R_b` as calculator values",
        "no extrapolation",
        "no rupture viability model",
        "no combined pinch-off + rupture viability model",
        "no coalescence model",
        "no path-independence or path-history model",
        "no Track A transfer-readiness integration",
    ]

    for phrase in required_phrases:
        assert phrase in combined_text


def test_citation_records_v020_doi_metadata() -> None:
    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    readiness = (ROOT / "docs" / "v0.2-release-readiness.md").read_text(
        encoding="utf-8"
    )

    assert "title: thalmetis-edr" in citation
    assert "given-names: Oliver" in citation
    assert "version: 0.2.0" in citation
    assert "doi: 10.5281/zenodo.19961963" in citation
    assert "10.5281/zenodo.19961963" in readme
    assert "10.5281/zenodo.19932773" in readme
    assert "McRae, O. (2026). thalmetis-edr (v0.2.0). Zenodo." in readme
    assert "doi: 10.5281/zenodo.19932774" not in citation
    assert "This is a v0.1.0 archive note" in readme
    assert "not presented as the current v0.2.0 package citation" in readme
    assert "post-release DOI metadata PR" in readiness
    assert "v0.2.0 Zenodo DOI: `10.5281/zenodo.19961963`" in readiness
    assert "all-versions / concept DOI: `10.5281/zenodo.19932773`" in readiness
    assert "Zenodo DOI will be added after the first GitHub release" not in citation
