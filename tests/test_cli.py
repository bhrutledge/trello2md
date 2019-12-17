import filecmp
import runpy
import stat
import subprocess
import sys
from importlib.metadata import entry_points
from pathlib import Path

import pytest

from trello2md import cli

TESTS_DIRNAME = Path(__file__).parent.resolve()
COMMAND_NAME = __name__

pytestmark = [
    pytest.mark.vcr(filter_headers=["authorization"]),
    pytest.mark.block_network,
]


# Autouse to ensure local config file isn't used by tests
@pytest.fixture(autouse=True)
def config_path(tmp_path, monkeypatch):
    config_path = tmp_path / "config"
    monkeypatch.setattr(cli, "CONFIG_PATH", config_path)
    return config_path


def test_write_credentials(config_path, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", [COMMAND_NAME, "auth"])

    def stub_get_credentials(app_name):
        assert app_name == "trello2md"
        return {"api_key": "api_key", "token": "oauth_token"}

    monkeypatch.setattr(cli.api, "get_credentials", stub_get_credentials)

    cli.main()

    assert config_path.read_text() == (
        "[credentials]\napi_key = api_key\ntoken = oauth_token\n\n"
    )

    assert stat.S_IMODE(config_path.stat().st_mode) == stat.S_IRUSR | stat.S_IWUSR

    captured = capsys.readouterr()
    assert str(config_path) in captured.out


@pytest.fixture
def config_file(config_path, monkeypatch):
    # Assuming sample board is public
    config_path.write_text("[credentials]\napi_key = \ntoken = \n\n")
    return config_path


def test_write_board(config_file, tmp_path, monkeypatch, capsys):
    url = "https://trello.com/b/WODq2cwg/sample-board"
    md_dirname = "sample-board"

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", [COMMAND_NAME, url])

    cli.main()

    captured = capsys.readouterr()

    md_filenames = [
        "index.md",
        "sample-card.md",
        "copied-card.md",
        "another-card.md",
        "another-card-1.md",
        "another-card-2.md",
    ]

    for filename, output in zip(md_filenames, captured.out.splitlines()):
        assert output.endswith(filename)

    match, mismatch, errors = filecmp.cmpfiles(
        tmp_path / md_dirname, TESTS_DIRNAME / md_dirname, md_filenames, shallow=False
    )
    assert set(match) == set(md_filenames)
    assert not (mismatch or errors)


@pytest.mark.parametrize(
    "url, md_filename",
    [
        pytest.param(
            "https://trello.com/c/HGYGb5iM/2-sample-card", "sample-card.md", id="sample"
        ),
        pytest.param("https://trello.com/c/9lhLVJz3", "copied-card.md", id="copied"),
    ],
)
def test_write_card(url, md_filename, config_file, monkeypatch, capsys):
    md_dirname = "sample-board"

    monkeypatch.setattr(sys, "argv", [COMMAND_NAME, url])

    cli.main()

    with open(TESTS_DIRNAME / md_dirname / md_filename) as f:
        sample_card = f.read()

    captured = capsys.readouterr()
    assert captured.out == sample_card


def test_help():
    # Using subprocess for simplicity and to smoke-test command line use
    result = subprocess.run(["trello2md", "-h"], check=True, capture_output=True)
    assert result.stdout.startswith(b"Export Trello boards and cards to Markdown.")


def test_no_arguments(config_file):
    # Using subprocess for simplicity and to smoke-test command line use
    result = subprocess.run(["trello2md"], capture_output=True)
    assert result.returncode > 0
    assert result.stderr.startswith(b"Usage")


def test_invalid_argument(config_file, monkeypatch):
    url = "https://trello.com/b"

    # Not using subprocess because it doesn't measure coverage (by default)

    monkeypatch.setattr(sys, "argv", [COMMAND_NAME, url])

    with pytest.raises(ValueError, match=url):
        cli.main()


def test_console_script(monkeypatch):
    # This is overkill with the subprocess tests, but it gives 100% branch coverage
    # of __main__.py, and it's an interesting example of using importlib

    # Don't leak loaded module into other tests (esp. test_run_as_module)
    monkeypatch.setattr(sys, "modules", dict(sys.modules))

    entry = next(
        x for x in entry_points()["console_scripts"] if x.name == "trello2md"
    )  # pragma: no cover

    console_script = entry.load()

    assert console_script == cli.main


def test_run_as_module(monkeypatch):
    monkeypatch.setattr(cli, "main", lambda: 1 / 0)

    with pytest.raises(ZeroDivisionError):
        runpy.run_module("trello2md", run_name="__main__")
