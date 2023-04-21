import pywhiten
import os
def test_copyconfig():
    pywhiten.cfg.make_config_file()
    assert os.path.exists("default.toml")
    os.remove("default.toml")