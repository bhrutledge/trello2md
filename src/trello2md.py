"""
Export Trello boards and cards to Markdown.

TODO:
- Show due, labels, members in list
- Save credentials to a file
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

import trello
import trello.util


def main() -> Optional[int]:
    """Print Markdown for a Trello object."""
    arg = sys.argv[1]

    if arg == "auth":
        get_authorization()
        return None

    client = trello.TrelloClient(
        api_key=os.environ["TRELLO_API_KEY"], token=os.environ["TRELLO2MD_TOKEN"],
    )

    url_match = re.search(r"trello\.com/([bc])/([\w]*)", arg)
    if not url_match:
        return None

    object_type, object_id = url_match.group(1, 2)

    if object_type == "b":
        board = client.get_board(object_id)
        with open_board(board) as file:
            write_board(board, file)
    else:
        card = client.get_card(object_id)
        write_card(card)

    return None


def get_authorization() -> None:
    """Prompt for and generate API credentials."""
    print("Go to the following link in your browser:")
    print("https://trello.com/app-key")
    print()

    api_key = input("Enter your API key: ")
    api_secret = getpass("Enter your API secret: ")
    print()

    access_token = trello.util.create_oauth_token(
        expiration="never", key=api_key, secret=api_secret, name=__name__, output=False
    )

    print()
    print("Set these environment variables:")
    print(f"TRELLO_API_KEY={api_key}")
    print(f"TRELLO2MD_TOKEN={access_token['oauth_token']}")


@contextmanager
def open_board(board: trello.Board) -> Iterator[IO[str]]:
    """Yield an open file in a new directory for a Trello board."""
    dirname = get_filename(get_slug(board.url))
    os.mkdir(dirname)
    os.chdir(dirname)
    filename = "index.md"
    print(f"{board.name:30.30} -> {os.path.join(dirname, filename)}")
    with open(filename, "w") as file:
        yield file


def write_board(board: trello.Board, file: Optional[IO[str]] = None) -> None:
    """Print Markdown for a Trello board."""
    print = partial(builtins.print, file=file if file else sys.stdout)

    print(f"# {board.name}")

    for lst in board.open_lists():
        print(f"\n## {lst.name}")

        cards = lst.list_cards()
        if cards:
            print()

        for card in cards:
            with open_card(card) as file:
                write_card(card, file=file)
                print(f"- [{card.name}]({file.name})")


@contextmanager
def open_card(card: trello.Card) -> Iterator[IO[str]]:
    """Yield an open file for a Trello card."""
    filename = get_filename(get_slug(card.url), ".md")
    print(f"{card.name:30.30} -> {filename}")
    with open(filename, "w") as file:
        yield file


def write_card(card: trello.Card, file: Optional[IO[str]] = None) -> Optional[str]:
    """Print Markdown for a Trello card."""
    print = partial(builtins.print, file=file if file else sys.stdout)

    print(f"# {card.name}")

    if card.due:
        print(f"\n**Due:** {card.due[:10]}")

    if card.description:
        print(f"\n{card.description}")

    for checklist in card.checklists:
        print(f"\n## {checklist.name}")

        if checklist.items:
            print()

        for item in checklist.items:
            print(f"- [{'x' if item['checked'] else ' '}] {item['name']}")

    if card.attachments:
        print("\n## Attachments\n")

    for attachment in card.attachments:
        if attachment["name"] == attachment["url"]:
            print(f"- <{attachment['url']}>")
        else:
            print(f"- [{attachment['name']}]({attachment['url']})")

    for comment in card.comments:
        print(
            "\n## Comment from"
            f" {comment['memberCreator']['fullName']}"
            f" on {comment['date'][:10]}\n"
        )
        print(comment["data"]["text"])

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


if __name__ == "__main__":
    sys.exit(main())
