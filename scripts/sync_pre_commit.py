# type: ignore
import argparse
import os
import pathlib
import subprocess
import sys

from pre_commit.clientlib import load_config
from pre_commit.repository import all_hooks
from pre_commit.store import Store

ROOT_PATH = pathlib.Path(__file__).parents[1]


def main():
    """Install pre-commit hooks in local virtual environment."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--verbose",
        help="increase output verbosity",
        dest="quiet",
        action="store_false",
    )
    args = parser.parse_args()

    os.environ["PIP_REQUIRE_VIRTUALENV"] = "true"

    config_file = ROOT_PATH / ".pre-commit-config.yaml"
    hooks = all_hooks(load_config(config_file), Store())

    for hook in hooks:
        # TODO: Avoid duplicate installs from same repo
        # e.g. pre-commit/pre-commit-hooks
        if hook.language == "python":
            install_python_hook(hook, args.quiet)
        else:
            print(f"Skipping {hook.id}: unsupported language '{hook.language}'")


def install_python_hook(hook, quiet=True):
    """Install a Python pre-commit hook."""
    print(f"Installing {hook.entry}")

    # Upgrading packages to use most recent source (instead of version)
    command = [
        "pip",
        "install",
        "--upgrade",
        hook.prefix.path(),
    ] + hook.additional_dependencies

    subprocess.run(command, check=True, capture_output=quiet)


if __name__ == "__main__":
    sys.exit(main())
