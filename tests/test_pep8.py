from pathlib import Path

import pycodestyle


def test_style_esrpoise():
    """
    Checks whether the Python files in the esrpoise package obey PEP8.
    """
    s = pycodestyle.StyleGuide()
    p = (Path(__file__).parents[1].resolve()) / "esrpoise"
    res = s.check_files([f for f in p.iterdir() if f.suffix == ".py"])
    assert res.total_errors == 0


def test_style_tests():
    """
    Checks whether the tests obey PEP8.
    """
    s = pycodestyle.StyleGuide()
    p = Path(__file__).parent
    res = s.check_files([f for f in p.iterdir() if f.suffix == ".py"])
    assert res.total_errors == 0
