from ..lambda1 import square, power_3


def test_one_equal_one():
    assert 4 == square(2)


def test_square_4():
    assert 16 == square(4)

def test_power_3_of_2():
    assert 8 == power_3(2)
