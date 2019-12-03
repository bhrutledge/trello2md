"""Friendlier APIs for Trello.

TODO:
- Replace py-trello with REST API calls
"""
import re
from dataclasses import dataclass, field
from functools import cached_property as property
from typing import Any, Dict, List, Optional, Union, cast

import trello


@dataclass
class Comment:
    """Friendlier API for a Trello comment."""

    obj: Dict[str, Any]

    @property
    def member(self) -> str:  # noqa: D102
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

    obj: Dict[str, Any]

    @property
    def url(self) -> str:  # noqa: D102
        return cast(str, self.obj["url"])

    @property
    def name(self) -> str:
        return cast(str, self.obj["name"])


@dataclass
class ChecklistItem:
    """Friendlier API for a Trello checklist item."""

    obj: Dict[str, Any]

    @property
    def name(self) -> str:  # noqa: D102
        return cast(str, self.obj["name"])

    @property
    def checked(self) -> bool:
        return cast(bool, self.obj["checked"])


@dataclass
class Checklist:
    """Friendlier API for a Trello checklist."""

    obj: trello.Checklist

    @property
    def name(self) -> str:  # noqa: D102
        return cast(str, self.obj.name)

    @property
    def items(self) -> List[ChecklistItem]:
        return [ChecklistItem(l) for l in self.obj.items]


@dataclass
class Card:
    """Friendlier API for a Trello card."""

    obj: trello.Card

    @property
    def url(self) -> str:  # noqa: D102
        return cast(str, self.obj.url)

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
    def labels(self) -> List[str]:
        return [f"`{l.name if l.name else l.color}`" for l in self.obj.labels or []]

    @property
    def members(self) -> List[str]:
        return [
            f"@{self.obj.board.client.get_member(i).username}"
            for i in self.obj.member_ids
        ]

    @property
    def meta(self) -> List[str]:
        return [x for x in [self.due_date, *self.members, *self.labels] if x]

    @property
    def checklists(self) -> List[Checklist]:
        return [Checklist(c) for c in self.obj.checklists]

    @property
    def attachments(self) -> List[Attachment]:
        return [Attachment(a) for a in self.obj.attachments]

    @property
    def comments(self) -> List[Comment]:
        return [Comment(c) for c in self.obj.comments]


# Not named `List` because that clashes with `typing.List`
@dataclass
class CardList:
    """Friendlier API for a Trello list."""

    obj: trello.List

    @property
    def name(self) -> str:  # noqa: D102
        return cast(str, self.obj.name)

    @property
    def cards(self) -> List[Card]:
        return [Card(l) for l in self.obj.list_cards()]


@dataclass
class Board:
    """Friendlier API for a Trello board."""

    obj: trello.Board

    @property
    def url(self) -> str:  # noqa: D102
        return cast(str, self.obj.url)

    @property
    def name(self) -> str:
        return cast(str, self.obj.name)

    @property
    def lists(self) -> List[CardList]:
        return [CardList(l) for l in self.obj.open_lists()]


@dataclass
class Client:
    """Friendlier API for the Trello client."""

    api_key: str
    token: str
    obj: trello.TrelloClient = field(init=False)

    def __post_init__(self) -> None:
        self.obj = trello.TrelloClient(api_key=self.api_key, token=self.token)

    def get_url(self, url: str) -> Optional[Union[Board, Card]]:
        """Return a Trello board or card from a URL."""
        url_match = re.search(r"trello\.com/([bc])/([\w]*)", url)
        if not url_match:
            return None

        object_type, object_id = url_match.group(1, 2)

        if object_type == "b":
            return Board(self.obj.get_board(object_id))

        return Card(self.obj.get_card(object_id))
