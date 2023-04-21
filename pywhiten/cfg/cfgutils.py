import os
import tomli

pkg_path = os.path.dirname(os.path.abspath(__file__))
default_cfg_path = os.path.join(pkg_path, 'default.toml')

with open(default_cfg_path, "rb") as f:
    default_cfg = tomli.load(f)

def make_config_file(path="./default.toml"):
    import shutil
    """
    Copies the default config file to somewhere (typically) outside the package files, so it can be edited by the user.
    Args:
        path (str): Path to copy the default configuration to

    Returns:

    """
    shutil.copyfile(default_cfg_path, path)
    print(f"[pywhiten] Made a copy of default configuration file at {path}!")