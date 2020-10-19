import area


def test_area_init():
    a = area.Area("Name")
    assert a.name == "Name"
    assert a.mode == "black"
    assert not a._isActive


def test_area_get_number_of_pixel():
    a = area.Area("Length")
    assert a.get_number_of_pixel() == 0

    a.add_strip(0, 10)
    assert a.get_number_of_pixel() == 10

    a.add_strip(10, 0)
    assert a.get_number_of_pixel() == 20
