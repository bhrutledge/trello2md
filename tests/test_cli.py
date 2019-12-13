import filecmp
import stat
import sys
from io import StringIO
from pathlib import Path

import pytest

from trello2md import cli


TESTS_DIRNAME = Path(__file__).parent.resolve()
COMMAND_NAME = __name__

pytestmark = [
    pytest.mark.vcr(filter_headers=["authorization"]),
    pytest.mark.block_network,
]


@pytest.mark.vcr(decode_compressed_response=True)
def test_write_credentials(tmp_path, monkeypatch, capsys):
    config_path = tmp_path / "config"
    monkeypatch.setattr(cli, "CONFIG_PATH", config_path)
    monkeypatch.setattr(sys, "argv", [COMMAND_NAME, "auth"])

    inputs = StringIO(
        # Enter your API key:
        "api_key\n"
        # Enter your API secret:
        "api_secret\n"
        # Have you authorized me? (y/n)
        "y\n"
        # What is the PIN?
        "verification\n"
    )
    monkeypatch.setattr(sys, "stdin", inputs)

    cli.main()

    assert config_path.read_text() == (
        "[credentials]\napi_key = api_key\ntoken = oauth_token\n\n"
    )

    assert stat.S_IMODE(config_path.stat().st_mode) == stat.S_IRUSR | stat.S_IWUSR

    captured = capsys.readouterr()
    assert str(config_path) in captured.out


@pytest.fixture
def config_file(record_mode, tmp_path, monkeypatch):
    if record_mode != "none":  # pragma: no cover
        return

    config_path = tmp_path / "config"
    config_path.write_text("[credentials]\napi_key = api_key\ntoken = oauth_token\n\n")
    monkeypatch.setattr(cli, "CONFIG_PATH", config_path)


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


def test_no_arguments(config_file, monkeypatch):
    monkeypatch.setattr(sys, "argv", [COMMAND_NAME])

    with pytest.raises(IndexError):
        cli.main()


def test_invalid_argument(config_file, monkeypatch):
    url = "https://trello.com/b"
    monkeypatch.setattr(sys, "argv", [COMMAND_NAME, url])

    with pytest.raises(ValueError, match=url):
        cli.main()
