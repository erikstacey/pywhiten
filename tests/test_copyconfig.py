import pywhiten
import os
def test_copyconfig():
    pywhiten.make_config_file()
    assert os.path.exists("default.toml")
    os.remove("default.toml")