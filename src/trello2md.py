"""
Transform Trello JSON exports to Markdown.

TODO:
- Move card printing to dedicated function
- Stub logic for writing board/list
- Generate safe filename from board/list/card title
- Implement board/list writing
- Look into https://github.com/sarumont/py-trello
- Use argparse

"""
import json
import sys
from operator import itemgetter
from typing import Optional


def main() -> Optional[int]:
    """Print Markdown for a Trello Card JSON export."""
    card_filename = sys.argv[1]

    with open(card_filename) as f:
        card = json.load(f)

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

    return None


if __name__ == "__main__":
    sys.exit(main())
