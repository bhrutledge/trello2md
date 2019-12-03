"""
Export Trello boards and cards to Markdown.

TODO:
- Add "## Comments" section
- Save credentials to a file
- Use package name in get_authorization
- Reconsider print partial
- Use argparse
- Option to remove existing board directory
- Download attachments?
"""
import builtins
import os
import re
import sys
from contextlib import contextmanager
from functools import partial
from getpass import getpass
from typing import IO, Iterator, Optional

from . import api


def main() -> Optional[int]:
    """Print Markdown for a Trello object."""
    arg = sys.argv[1]

    if arg == "auth":
        get_authorization()
        return None

    client = api.Client(
        api_key=os.environ["TRELLO_API_KEY"], token=os.environ["TRELLO2MD_TOKEN"],
    )

    obj = client.get_url(arg)

    if isinstance(obj, api.Board):
        with open_board(obj) as file:
            write_board(obj, file)

    elif isinstance(obj, api.Card):
        write_card(obj)

    return None


def get_authorization() -> None:
    """Prompt for and generate API credentials."""
    from trello.util import create_oauth_token

    print("Go to the following link in your browser:")
    print("https://trello.com/app-key")
    print()

    api_key = input("Enter your API key: ")
    api_secret = getpass("Enter your API secret: ")
    print()

    access_token = create_oauth_token(
        expiration="never",
        key=api_key,
        secret=api_secret,
        name="trello2md",
        output=False,
    )

    print()
    print("Set these environment variables:")
    print(f"TRELLO_API_KEY={api_key}")
    print(f"TRELLO2MD_TOKEN={access_token['oauth_token']}")


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
                meta = ", ".join(card.meta)
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

    if card.meta:
        print()
        print(", ".join(card.meta))

    if card.description:
        print(f"\n{card.description}")

    for checklist in card.checklists:
        print(f"\n## {checklist.name}")

        if checklist.items:
            print()

        for item in checklist.items:
            print(f"- [{'x' if item.checked else ' '}] {item.name}")

    if card.attachments:
        print("\n## Attachments\n")

    for attachment in card.attachments:
        if attachment.name == attachment.url:
            print(f"- <{attachment.url}>")
        else:
            print(f"- [{attachment.name}]({attachment.url})")

    for comment in card.comments:
        print(f"\n## Comment from {comment.member} on {comment.date}\n")
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
