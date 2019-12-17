"""Export Trello boards and cards to Markdown.

Usage:
  trello2md auth
  trello2md <url>
  trello2md -h | --help | --version

Arguments:
  auth      Authorize use of the Trello API
  <url>     The URL for a Trello board or card

"""
import builtins
import os
import re
import stat
import sys
from configparser import ConfigParser
from contextlib import contextmanager
from functools import partial
from importlib import metadata
from pathlib import Path
from typing import IO, Iterator, Optional

from docopt import docopt

from . import api

COMMAND_NAME = "trello2md"
CONFIG_PATH = Path.home() / ".config" / COMMAND_NAME


def main() -> Optional[str]:
    """Process command line arguments."""
    args = docopt(__doc__, version=metadata.version(COMMAND_NAME))

    if args["auth"]:
        write_credentials()
    else:
        write_url(args["<url>"])

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


def write_url(url: str) -> None:
    """Print Markdown from a Trello URL."""
    config = ConfigParser()

    with open(CONFIG_PATH) as config_file:
        config.read_file(config_file)

    client = api.Client(config["credentials"])

    obj = client.get_url(url)

    if isinstance(obj, api.Board):
        with open_board(obj) as file:
            write_board(obj, file)
    else:
        write_card(obj)


@contextmanager
def open_board(board: api.Board) -> Iterator[IO[str]]:
    """Yield an open file in a new directory for a Trello board."""
    dirname = get_filename(board.slug)
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

                print(f"- [{card.name}]({file.name})", end="")
                print(f" {meta}" if (meta := get_card_meta(card)) else "")


@contextmanager
def open_card(card: api.Card) -> Iterator[IO[str]]:
    """Yield an open file for a Trello card."""
    filename = get_filename(card.slug, ".md")
    print(f"{card.name:30.30} -> {filename}")
    with open(filename, "w") as file:
        yield file


def write_card(card: api.Card, file: Optional[IO[str]] = None) -> None:
    """Print Markdown for a Trello card."""
    print = partial(builtins.print, file=file if file else sys.stdout)

    print(f"# {card.name}")

    if meta := get_card_meta(card):
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


def get_filename(slug: str, ext: str = "") -> str:
    """Return a unique filename."""
    # Remove numeric prefix from card slug
    slug = re.sub(r"^\d+-", "", slug)

    filename = slug + ext
    suffix = 0

    while os.path.exists(filename):
        filename = f"{slug}-{(suffix := suffix + 1)}{ext}"

    return filename


def get_card_meta(card: api.Card) -> str:
    """Return metadata for a Trello card, separated by commas."""
    members = [f"@{x}" for x in card.members]
    labels = [f"`{x}`" for x in card.labels]
    return ", ".join([x for x in [card.due_date, *members, *labels] if x])
