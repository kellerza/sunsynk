"""Test sensor definitions."""

from sunsynk.definitions import import_all_defs, import_defs


def test_import_defs() -> None:
    """Test importing sensors."""
    libs = (
        "single_phase",
        "three_phase_hv",
        "three_phase_lv",
        "micro_hybrid_ess",
    )
    for lib in libs:
        defs = import_defs(lib)
        assert len(defs.all) > 50
        assert defs.rated_power


def test_three_phase_grid_standard() -> None:
    """Grid standard 27 as reported in #711."""
    for lib in ("three_phase_lv", "three_phase_hv"):
        sen = import_defs(lib).all["grid_standard"]
        assert sen.reg_to_value((27,)) == "EN50549_1"


def test_all_defs() -> None:
    """Test all sensor definitions."""
    all_defs = import_all_defs()
    assert len(all_defs) == 5
