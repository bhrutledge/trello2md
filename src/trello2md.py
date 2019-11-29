"""
Transform Trello JSON exports to Markdown.

TODO:
- Stub logic for writing board/list
- Generate safe filename from board/list/card title
- Write card to file
- Implement board/list writing
- Look into https://github.com/sarumont/py-trello
- Use argparse
"""
import json
import sys
from operator import itemgetter
from typing import Any, Dict, Optional


def main() -> Optional[int]:
    """Print Markdown for a Trello JSON export."""
    filename = sys.argv[1]

    with open(filename) as f:
        export = json.load(f)

    if "/b/" in export["shortUrl"]:
        write_board(export)
    elif "/c/" in export["shortUrl"]:
        write_card(export)

    return None


def write_board(board: Dict[str, Any]) -> None:
    """Write Markdown for a Trello Board JSON export."""
    print("Lists:")
    for lst in board["lists"]:
        print(lst["name"])

    print()

    print("Cards:")
    for card in board["cards"]:
        print(card["name"])


def write_card(card: Dict[str, Any]) -> None:
    """Write Markdown for a Trello Card JSON export."""
    print(f"# {card['name']}")

    if card["due"]:
        print(f"\n**Due:** {card['due'][:10]}")

    if card["desc"]:
        print(f"\n{card['desc']}")

    for checklist in card["checklists"]:
        print(f"\n## {checklist['name']}\n")
        for item in sorted(checklist["checkItems"], key=itemgetter("pos")):
            print(f"- [{'x' if item['state'] == 'complete' else ' '}] {item['name']}")

    deleted_attachment_ids = {
        x["data"]["attachment"]["id"]
        for x in card["actions"]
        if x["type"] == "deleteAttachmentFromCard"
    }

    attachments = [
        x["data"]["attachment"]
        for x in card["actions"]
        if x["type"] == "addAttachmentToCard"
        and x["data"]["attachment"]["id"] not in deleted_attachment_ids
    ]

    if attachments:
        print("\n## Attachments\n")

    for attachment in attachments:
        if attachment["name"] == attachment["url"]:
            print(f"- <{attachment['url']}>")
        else:
            print(f"- [{attachment['name']}]({attachment['url']})")

    comments = [x for x in card["actions"] if x["type"] == "commentCard"]

    for comment in comments:
        print(
            "\n## Comment from"
            f" {comment['memberCreator']['fullName']}"
            f" on {comment['date'][:10]}\n"
        )
        print(comment["data"]["text"])


if __name__ == "__main__":
    sys.exit(main())
