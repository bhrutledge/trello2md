"""Export Trello boards and cards to Markdown."""
import builtins
import os
import re
import stat
import sys
from configparser import ConfigParser
from contextlib import contextmanager
from functools import partial
from pathlib import Path
from typing import IO, Iterator, Optional

from . import api

COMMAND_NAME = "trello2md"
CONFIG_PATH = Path.home() / ".config" / COMMAND_NAME


def main() -> Optional[int]:
    """Process command line arguments."""
    arg = sys.argv[1]

    if arg == "auth":
        write_credentials()
    else:
        write_object_from_url(arg)

    return None


def write_credentials() -> None:
    """Prompt for and save API credentials."""
    config = ConfigParser()
    config["credentials"] = api.get_credentials(COMMAND_NAME)

    with open(CONFIG_PATH, "w") as config_file:
        config.write(config_file)

    CONFIG_PATH.chmod(stat.S_IRUSR | stat.S_IWUSR)

    print()
    print(f"Credentials saved to {CONFIG_PATH}")


def write_object_from_url(url: str) -> None:
    """Print Markdown for a Trello object."""
    config = ConfigParser()

    with open(CONFIG_PATH) as config_file:
        config.read_file(config_file)

    client = api.Client(config["credentials"])

    obj = client.get_url(url)

    if isinstance(obj, api.Board):
        with open_board(obj) as file:
            write_board(obj, file)

    elif isinstance(obj, api.Card):
        write_card(obj)


@contextmanager
def open_board(board: api.Board) -> Iterator[IO[str]]:
    """Yield an open file in a new directory for a Trello board."""
    dirname = get_filename(get_slug(board.url))
    os.mkdir(dirname)
    os.chdir(dirname)

    filename = "index.md"
    print(f"{board.name:30.30} -> {os.path.join(dirname, filename)}")
    with open(filename, "w") as file:
        yield file


def write_board(board: api.Board, file: Optional[IO[str]] = None) -> None:
    """Print Markdown for a Trello board."""
    print = partial(builtins.print, file=file if file else sys.stdout)

    print(f"# {board.name}")

    for lst in board.lists:
        print(f"\n## {lst.name}")

        if lst.cards:
            print()

        for card in lst.cards:
            with open_card(card) as file:
                write_card(card, file=file)

                link = f"- [{card.name}]({file.name})"
                meta = get_card_meta(card)
                print(f"{link} {meta}" if meta else link)


@contextmanager
def open_card(card: api.Card) -> Iterator[IO[str]]:
    """Yield an open file for a Trello card."""
    filename = get_filename(get_slug(card.url), ".md")
    print(f"{card.name:30.30} -> {filename}")
    with open(filename, "w") as file:
        yield file


def write_card(card: api.Card, file: Optional[IO[str]] = None) -> Optional[str]:
    """Print Markdown for a Trello card."""
    print = partial(builtins.print, file=file if file else sys.stdout)

    print(f"# {card.name}")

    meta = get_card_meta(card)
    if meta:
        print()
        print(meta)

    if card.description:
        print(f"\n{card.description}")

    for checklist in card.checklists:
        print(f"\n## {checklist.name}")

        if checklist.items:
            print()

        for item in checklist.items:
            print(f"- [{'x' if item.checked else ' '}] {item.name}")

    if card.attachments:
        print("\n## Attachments")
        print()

    for attachment in card.attachments:
        if attachment.name == attachment.url:
            print(f"- <{attachment.url}>")
        else:
            print(f"- [{attachment.name}]({attachment.url})")

    if card.comments:
        print("\n## Comments")

    for comment in card.comments:
        print(f"\n### {comment.member} on {comment.date}\n")
        print(comment.body)

    return None


def get_slug(url: str) -> str:
    """Return a slug derived from a Trello object URL."""
    match = re.search(r"trello\.com.*/[\d-]*(.*)$", url)
    if match is None:
        raise ValueError(f"Invalid URL: {url}")

    return match.group(1)


def get_filename(slug: str, ext: str = "") -> str:
    """Return a unique filename."""
    i = 0
    filename = slug + ext

    while os.path.exists(filename):
        i += 1
        filename = f"{slug}-{i}" + ext

    return filename


def get_card_meta(card: api.Card) -> str:
    """Return metadata for a Trello card, separated by commas."""
    members = [f"@{m}" for m in card.members]
    labels = [f"`{l}`" for l in card.labels]
    return ", ".join([x for x in [card.due_date, *members, *labels] if x])
