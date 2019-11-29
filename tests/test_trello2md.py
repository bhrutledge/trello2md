# type: ignore
import pathlib
import sys

import pytest

import trello2md


@pytest.mark.parametrize(
    "card_path",
    [
        "sample-card.json",
        pytest.param(
            "copied-card.json", marks=pytest.mark.xfail(reason="not supported"),
        ),
    ],
)
def test_write_card(card_path, monkeypatch, capsys):
    testdir = pathlib.Path(__file__).parent.resolve()
    monkeypatch.setattr(sys, "argv", [trello2md.__file__, testdir / card_path])

    trello2md.main()

    with open(testdir / card_path.replace(".json", ".md")) as f:
        sample_card = f.read()

    captured = capsys.readouterr()
    assert captured.out == sample_card
