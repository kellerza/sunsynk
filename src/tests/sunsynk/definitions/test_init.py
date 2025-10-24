"""Test sensor definitions."""

from sunsynk.definitions import import_all_defs, import_defs


def test_import_defs() -> None:
    """Test importing sensors."""
    libs = (
        "single_phase",
        "three_phase_hv",
        "three_phase_lv",
    )
    for lib in libs:
        defs = import_defs(lib)
        assert len(defs.all) > 50
        assert defs.rated_power


def test_all_defs() -> None:
    """Test all sensor definitions."""
    all_defs = import_all_defs()
    assert len(all_defs) == 4
