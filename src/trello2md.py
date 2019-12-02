"""
Export Trello boards and cards to Markdown.

TODO:
- Use cached_property (requires 3.8)
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
from dataclasses import dataclass
from functools import partial
from getpass import getpass
from typing import Any, Dict, IO, Iterator, List, Optional, cast

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
        card = CardWrapper(client.get_card(object_id))
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

        cards = [CardWrapper(c) for c in lst.list_cards()]
        if cards:
            print()

        for card in cards:
            with open_card(card) as file:
                write_card(card, file=file)

                link = f"- [{card.name}]({file.name})"
                meta = ", ".join(card.meta)
                print(f"{link} {meta}" if meta else link)


@dataclass
class CardWrapper:
    """Friendlier API for a Trello card."""

    card: trello.Card

    # HACK: Avoid spurious D102 from pydocstyle on first @property
    def __post_init__(self) -> None:
        pass

    @property
    def url(self) -> str:
        return cast(str, self.card.url)

    @property
    def name(self) -> str:
        return cast(str, self.card.name)

    @property
    def description(self) -> str:
        return cast(str, self.card.description)

    @property
    def checklists(self) -> List[trello.Checklist]:
        return cast(List[trello.Checklist], self.card.checklists)

    @property
    def attachments(self) -> List[Dict[str, Any]]:
        return cast(List[Dict[str, Any]], self.card.attachments)

    @property
    def comments(self) -> List[Dict[str, Any]]:
        return [
            {
                "member": c["memberCreator"]["username"],
                "date": c["date"][:10],
                "text": c["data"]["text"],
            }
            for c in self.card.comments
        ]

    @property
    def due_date(self) -> Optional[str]:
        return self.card.due[:10] if self.card.due else None

    @property
    def labels(self) -> List[str]:
        return [f"`{l.name if l.name else l.color}`" for l in self.card.labels or []]

    @property
    def members(self) -> List[str]:
        return [
            f"@{self.card.board.client.get_member(i).username}"
            for i in self.card.member_ids
        ]

    @property
    def meta(self) -> List[str]:
        return [x for x in [self.due_date, *self.members, *self.labels] if x]


@contextmanager
def open_card(card: CardWrapper) -> Iterator[IO[str]]:
    """Yield an open file for a Trello card."""
    filename = get_filename(get_slug(card.url), ".md")
    print(f"{card.name:30.30} -> {filename}")
    with open(filename, "w") as file:
        yield file


def write_card(card: CardWrapper, file: Optional[IO[str]] = None) -> Optional[str]:
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
            print(f"- [{'x' if item['checked'] else ' '}] {item['name']}")

    if card.attachments:
        print("\n## Attachments\n")

    for attachment in card.attachments:
        if attachment["name"] == attachment["url"]:
            print(f"- <{attachment['url']}>")
        else:
            print(f"- [{attachment['name']}]({attachment['url']})")

    for comment in card.comments:
        print(f"\n## Comment from {comment['member']} on {comment['date']}\n")
        print(comment["text"])

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
