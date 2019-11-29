# type: ignore
import pathlib
import sys

import trello2md


def test_sample_card(monkeypatch, capsys):
    testdir = pathlib.Path(__file__).parent.resolve()
    monkeypatch.setattr(sys, "argv", [trello2md.__file__, testdir / "sample-card.json"])

    trello2md.main()

    with open(testdir / "sample-card.md") as f:
        sample_card = f.read()

    captured = capsys.readouterr()
    assert captured.out == sample_card
