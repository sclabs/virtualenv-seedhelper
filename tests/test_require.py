import os
import subprocess

from virtualenv_seedhelper import config, require

REQUIREMENT_STR = "requests==2.31.0"


def test_example():
    # run seedhelper config and seedhelper download
    config()
    require(REQUIREMENT_STR)

    # copy the current env
    env = os.environ.copy()

    # delete keys that tox sets
    for key in list(env.keys()):
        if key.startswith("TOX_"):
            del env[key]

    # run tox from the example directory with the copied env
    subprocess.run(["tox", "-r"], cwd="./examples/require", env=env, check=True)
