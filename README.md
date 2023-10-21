virtualenv-seedhelper
=====================

A virtualenv seeder to seed wheels from a folder

Quick start
-----------

### Install in system python environment

    python3 -m pip install virtualenv-seedhelper

### Configure virtualenv to always use seedhelper

    seedhelper config

Note that this overwrites `virtualenv.ini` if it already exists.

### Add wheels to SEEDHELPER_WHEELS_DIR one at a time by URL

    seedhelper download https://files.pythonhosted.org/packages/f1/13/63c0a02c44024ee16f664e0b36eefeb22d54e93531630bd99e237986f534/cowsay-6.1-py3-none-any.whl

### Create a new virtualenv

    python3 -m virtualenv venv

### Verify that the new virtualenv has the wheels installed in it

    $ venv/bin/pip list
    Package    Version
    ---------- -------
    cowsay     6.1
    pip        23.2.1
    setuptools 68.2.2
    wheel      0.41.2

### What if we want to seed a package with dependencies?

Instead of looking up and downloading wheel URLs one by one, we can use
`seedhelper require` to download the wheels for all the dependencies of a
requirement, placing all of their wheels in the `SEEDHELPER_WHEELS_DIR` so that
they all get seeded into newly-created virtualenvs.

    seedhelper require requests==2.31.0

After this, we can make a new virtualenv

    python3 -m virtualenv venv

and verify that it has all the dependencies installed

    $ venv/bin/pip list
    Package            Version
    ------------------ ---------
    certifi            2023.7.22
    charset-normalizer 3.3.0
    idna               3.4
    pip                23.2.1
    requests           2.31.0
    setuptools         68.2.2
    urllib3            2.0.7
    wheel              0.41.2

and we can import the package in the venv

    venv/bin/python -c 'import requests'

Config
------

### SEEDHELPER_WHEELS_DIR

This is where seedhelper will download wheels to. It defaults to
`~/Library/Application Support/virtualenv/seedhelper_wheels` (or the
corresponding location on your specific platform as provided by
`platformdirs.user_config_dir()`). You can override it by setting an
environment variable called `SEEDHELPER_WHEELS_DIR`.

### VIRTUALENV_CONFIG_FILE

This is where virtualenv (and seedhelper) will look for `virtualenv.ini`. It
defaults to `~/Library/Application Support/virtualenv/virtualenv.ini` (or the
corresponding location on your specific platform as provided by
`platformdirs.user_config_dir()`). You can override it by setting an
environment variable called `VIRTUALENV_CONFIG_FILE`.

Motivation
----------

The goal is to make it possible to include a set of wheels in every virtualenv
created. This is especially useful when the system-wide pip configuration
assumes that certain packages, such as keyring backends needed to interact with
a private package index, will always be available before pip runs. Without a
seeder, you cannot use pip to install the keyring because pip itself needs the
keyring to be already installed in order to function at all.
