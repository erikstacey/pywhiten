import tomli
import os
from pywhiten.pwio.OutputManager import OutputManager
import shutil
def test_OutputManager_tree_setup():
    default_config = os.getcwd()+"/pywhiten/cfg/default.toml"
    with open(default_config, "rb") as f:
        cfg = tomli.load(f)

    test_output_manager = OutputManager(cfg=cfg)
    if os.path.exists(os.getcwd()+"/pw_out"):
        shutil.rmtree(os.getcwd()+"/pw_out")
        return 0
    else:
        return 1