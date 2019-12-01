# type: ignore
import filecmp
import pathlib
import sys

import pytest

import trello2md


TESTS_DIRNAME = pathlib.Path(__file__).parent.resolve()
SCRIPT_NAME = trello2md.__file__


def test_write_board(tmp_path, monkeypatch, capsys):
    url = "https://trello.com/b/WODq2cwg/sample-board"
    md_dirname = "sample-board"

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", [SCRIPT_NAME, url])

    trello2md.main()

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
        ("https://trello.com/c/HGYGb5iM/2-sample-card", "sample-card.md"),
        ("https://trello.com/c/9lhLVJz3", "copied-card.md"),
    ],
)
def test_write_card(url, md_filename, monkeypatch, capsys):
    md_dirname = "sample-board"
    monkeypatch.setattr(sys, "argv", [SCRIPT_NAME, url])

    trello2md.main()

    with open(TESTS_DIRNAME / md_dirname / md_filename) as f:
        sample_card = f.read()

    captured = capsys.readouterr()
    assert captured.out == sample_card
