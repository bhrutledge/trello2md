"""Friendlier APIs for Trello."""
import re
from abc import ABC
from dataclasses import dataclass, field
from functools import cached_property as property
from typing import Any, Mapping, Optional, Sequence, Union, cast

import trello


@dataclass
class Comment:
    """Friendlier API for a Trello comment."""

    obj: Mapping[str, Any]

    @property
    def member(self) -> str:
        return cast(str, self.obj["memberCreator"]["username"])

    @property
    def date(self) -> str:
        return cast(str, self.obj["date"][:10])

    @property
    def body(self) -> str:
        return cast(str, self.obj["data"]["text"])


@dataclass
class Attachment:
    """Friendlier API for a Trello attachment."""

    obj: Mapping[str, Any]

    @property
    def url(self) -> str:
        return cast(str, self.obj["url"])

    @property
    def name(self) -> str:
        return cast(str, self.obj["name"])


@dataclass
class ChecklistItem:
    """Friendlier API for a Trello checklist item."""

    obj: Mapping[str, Any]

    @property
    def name(self) -> str:
        return cast(str, self.obj["name"])

    @property
    def checked(self) -> bool:
        return cast(bool, self.obj["checked"])


@dataclass
class Checklist:
    """Friendlier API for a Trello checklist."""

    obj: trello.Checklist

    @property
    def name(self) -> str:
        return cast(str, self.obj.name)

    @property
    def items(self) -> Sequence[ChecklistItem]:
        return [ChecklistItem(x) for x in self.obj.items]


class Exportable(ABC):
    """Base class for an exportable Trello object."""

    obj: Any

    @property
    def url(self) -> str:
        return cast(str, self.obj.url)

    @property
    def slug(self) -> str:
        return self.url.split("/")[-1]


@dataclass
class Card(Exportable):
    """Friendlier API for a Trello card."""

    obj: trello.Card

    @property
    def name(self) -> str:
        return cast(str, self.obj.name)

    @property
    def description(self) -> str:
        return cast(str, self.obj.description)

    @property
    def due_date(self) -> Optional[str]:
        return self.obj.due[:10] if self.obj.due else None

    @property
    def labels(self) -> Sequence[str]:
        return [x.name if x.name else x.color for x in (self.obj.labels or [])]

    @property
    def members(self) -> Sequence[str]:
        return [
            self.obj.board.client.get_member(x).username for x in self.obj.member_ids
        ]

    @property
    def checklists(self) -> Sequence[Checklist]:
        return [Checklist(x) for x in self.obj.checklists]

    @property
    def attachments(self) -> Sequence[Attachment]:
        return [Attachment(x) for x in self.obj.attachments]

    @property
    def comments(self) -> Sequence[Comment]:
        return [Comment(x) for x in self.obj.comments]


@dataclass
class CardList:
    """Friendlier API for a Trello list.

    Not named `List` because that clashes with `typing.List`.
    """

    obj: trello.List

    @property
    def name(self) -> str:
        return cast(str, self.obj.name)

    @property
    def cards(self) -> Sequence[Card]:
        return [Card(x) for x in self.obj.list_cards()]


@dataclass
class Board(Exportable):
    """Friendlier API for a Trello board."""

    obj: trello.Board

    @property
    def name(self) -> str:
        return cast(str, self.obj.name)

    @property
    def lists(self) -> Sequence[CardList]:
        return [CardList(x) for x in self.obj.open_lists()]


Config = Mapping[str, str]


@dataclass
class Client:
    """Friendlier API for the Trello client."""

    credentials: Config
    obj: trello.TrelloClient = field(init=False)

    def __post_init__(self) -> None:
        self.obj = trello.TrelloClient(**self.credentials)

    def get_url(self, url: str) -> Union[Board, Card]:
        """Return a Trello board or card from a URL."""
        url_match = re.search(r"trello\.com/([bc])/([\w]*)", url)
        if not url_match:
            raise ValueError(f"Invalid URL: {url}")

        object_type, object_id = url_match.group(1, 2)

        if object_type == "b":
            return Board(self.obj.get_board(object_id))

        return Card(self.obj.get_card(object_id))


def get_credentials(app_name: str) -> Config:
    """Prompt for and generate API credentials."""
    print("Go to the following link in your browser:")
    print("https://trello.com/app-key")
    print()

    api_key = input("Enter your API key: ")
    api_secret = input("Enter your API secret: ")
    print()

    access_token = trello.util.create_oauth_token(
        expiration="never",
        scope="read",
        key=api_key,
        secret=api_secret,
        name=app_name,
        output=False,
    )

    return {
        "api_key": api_key,
        "token": access_token["oauth_token"],
    }
