from __future__ import annotations

import os
from pathlib import Path

from pip._internal.cache import WheelCache
from pip._internal.commands.install import InstallCommand
from pip._internal.locations import USER_CACHE_DIR
from pip._internal.operations.build.build_tracker import get_build_tracker
from pip._internal.req import InstallRequirement
from pip._internal.utils.temp_dir import (
    TempDirectory,
    global_tempdir_manager,
    tempdir_registry,
)
from pip._vendor.packaging.requirements import Requirement
from platformdirs import user_config_dir
from virtualenv.config.cli.parser import VirtualEnvOptions
from virtualenv.seed.embed.via_app_data.via_app_data import FromAppData
from virtualenv.seed.wheels import Version
from virtualenv.seed.wheels.embed import BUNDLE_SUPPORT

VIRTUALENV_CONFIG_DIR = Path(user_config_dir(appname="virtualenv", appauthor="pypa"))
SEEDHELPER_WHEELS_DIR = Path(
    os.environ.get("SEEDHELPER_WHEELS_DIR", VIRTUALENV_CONFIG_DIR / "seedhelper_wheels")
)
VIRTUALENV_CONFIG_FILE = Path(
    os.environ.get("VIRTUALENV_CONFIG_FILE", VIRTUALENV_CONFIG_DIR / "virtualenv.ini")
)
VIRTUALENV_INI_CONTENT = (
    f"[virtualenv]\nseeder = seedhelper\nextra_search_dir = {SEEDHELPER_WHEELS_DIR}"
)


def get_seedhelper_packages() -> set[str]:
    """
    Get a set of the package names for all wheels in the SEEDHELPER_WHEELS_DIR.
    """
    if not SEEDHELPER_WHEELS_DIR.exists():
        return set()
    return {
        wheel.name.split("-", 1)[0]
        for wheel in SEEDHELPER_WHEELS_DIR.iterdir()
        if wheel.name.endswith(".whl")
    }


class SeedHelper(FromAppData):  # type: ignore
    def __init__(self, options: VirtualEnvOptions) -> None:
        # get the list of wheels to seed from the seedhelper_wheels directory
        self.seedhelper_packages = get_seedhelper_packages()

        # monkey patch BUNDLE_SUPPORT to dodge a TypeError
        for py_version in BUNDLE_SUPPORT.keys():
            for package in self.seedhelper_packages:
                BUNDLE_SUPPORT[py_version][package] = ""

        # create no_{package} and {package}_version attributes for each package
        for package in self.seedhelper_packages:
            setattr(self, f"no_{package}", False)
            setattr(self, f"{package}_version", Version.bundle)

        # call superclass init
        super().__init__(options)

    @classmethod
    def distributions(cls) -> dict[str, Version]:
        # override distributions() to add all seedhelper packages
        return {
            **super().distributions(),
            **{package: Version.bundle for package in get_seedhelper_packages()},
        }


def config() -> None:
    """
    Overwrite virtualenv.ini with the recommended configuration for seedhelper.
    """
    VIRTUALENV_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(VIRTUALENV_CONFIG_FILE, "w") as f:
        f.write(VIRTUALENV_INI_CONTENT)


def download(wheel_url: str) -> None:
    """
    Download a wheel from a URL to the seedhelper_wheels directory.
    """
    from urllib.request import urlretrieve

    SEEDHELPER_WHEELS_DIR.mkdir(parents=True, exist_ok=True)
    urlretrieve(wheel_url, SEEDHELPER_WHEELS_DIR / Path(wheel_url).name)


def require(requirement_str: str) -> None:
    """
    Download all required wheels to statisfy one requirement.
    """
    for requirement in resolve_requirement_str(requirement_str):
        download(requirement.link.url)  # type: ignore


def main() -> None:
    """
    CLI helpers for seedhelper.
    """
    from fire import Fire

    Fire({"config": config, "download": download, "require": require})


def resolve_requirement_str(requirement_str: str) -> list[InstallRequirement]:
    """
    Resolve a requirement string to a list of InstallRequirements.
    """
    cmd = InstallCommand(name="mock", summary="mock")
    with cmd.main_context():
        options, _ = cmd.parse_args([])
        cmd.enter_context(tempdir_registry())
        cmd.enter_context(global_tempdir_manager())
        session = cmd.get_default_session(options)
        finder = cmd._build_package_finder(options, session)
        build_tracker = cmd.enter_context(get_build_tracker())
        directory = TempDirectory(kind="wheel", globally_managed=True)
        wheel_cache = WheelCache(USER_CACHE_DIR)
        preparer = cmd.make_requirement_preparer(
            temp_build_dir=directory,
            options=options,
            build_tracker=build_tracker,
            session=session,
            finder=finder,
            use_user_site=False,
        )
        resolver = cmd.make_resolver(
            preparer=preparer,
            finder=finder,
            options=options,
            wheel_cache=wheel_cache,
        )
        install_req = InstallRequirement(Requirement(requirement_str), comes_from=None)
        req_set = resolver.resolve([install_req], check_supported_wheels=True)
        return [x for x in req_set.requirements.values()]


if __name__ == "__main__":
    main()
