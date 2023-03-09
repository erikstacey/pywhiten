import pywhiten

def test_Frequency():
    test_object_noidx = pywhiten.data.Frequency(1.2, 1.3, 0.3, 0)
    assert test_object_noidx.get_parameters() == (1.2, 1.3, 0.3)
    test_object_noidx.update(2.2, -2.3, 0.3)
    assert test_object_noidx.get_parameters() == (2.2, -2.3, 0.3)
    test_object_noidx.adjust_params()
    # accounts for floating point error. In reality we don't want to throw this out like this.
    test_object_noidx.p = round(test_object_noidx.p, 5)
    assert test_object_noidx.get_parameters() == (2.2, 2.3, 0.8)
    test_object_noidx.update(2.2, -2.3, 55.3)
    test_object_noidx.adjust_params()
    test_object_noidx.p = round(test_object_noidx.p, 5)
    assert test_object_noidx.get_parameters() == (2.2, 2.3, 0.8)

    # check to make sure we still have original parameters
    assert test_object_noidx.f0 == 1.2
    assert test_object_noidx.a0 == 1.3
    assert test_object_noidx.p0 == 0.3


    test_object_widx = pywhiten.data.Frequency(1.2, 1.3, 0.3, 0, n=1)