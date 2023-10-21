import os
import subprocess

from virtualenv_seedhelper import config, download

WHEEL_URL = (
    "https://files.pythonhosted.org/packages/f1/13/"
    "63c0a02c44024ee16f664e0b36eefeb22d54e93531630bd99e237986f534/"
    "cowsay-6.1-py3-none-any.whl"
)


def test_example():
    # run seedhelper config and seedhelper download
    config()
    download(WHEEL_URL)

    # copy the current env
    env = os.environ.copy()

    # delete keys that tox sets
    for key in list(env.keys()):
        if key.startswith("TOX_"):
            del env[key]

    # run tox from the example directory with the copied env
    subprocess.run(["tox", "-r"], cwd="./examples/download", env=env, check=True)
