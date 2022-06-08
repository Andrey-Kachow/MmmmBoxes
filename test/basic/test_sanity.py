import pytest

def test_simple():
    assert 2 + 2 == 4

def test_div_zero():
    with pytest.raises(ZeroDivisionError):
        1 / 0