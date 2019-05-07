import json
from operator import itemgetter
from pprint import pprint
import sys


def main():
    # TODO: Use argparse
    # TODO: Get JSON via card URL (needs login via CLI))
    # Or, jook into https://github.com/sarumont/py-trello
    card_filename = sys.argv[1]

    with open(card_filename) as f:
        card = json.load(f)

    print(f"# {card['name']}")

    if card['due']:
        print(f"\n**Due:** {card['due'][:10]}")

    if card['desc']:
        print(f"\n{card['desc']}")

    for checklist in card['checklists']:
        print(f"\n## {checklist['name']}\n")
        for item in sorted(checklist['checkItems'], key=itemgetter('pos')):
            print(f"- [{'x' if item['state'] == 'complete' else ' '}] {item['name']}")

    deleted_attachment_ids = {
        x['data']['attachment']['id'] for x in card['actions']
        if x['type'] == 'deleteAttachmentFromCard'
    }

    attachments = [
        x['data']['attachment'] for x in card['actions']
        if x['type'] == 'addAttachmentToCard'
        and x['data']['attachment']['id'] not in deleted_attachment_ids
    ]

    if attachments:
        print('\n## Attachments\n')

    for attachment in attachments:
        if attachment['name'] == attachment['url']:
            print(f"- <{attachment['url']}>")
        else:
            print(f"- [{attachment['name']}]({attachment['url']})")

    comments = [
        x for x in card['actions']
        if x['type'] == 'commentCard'
    ]

    for comment in comments:
        print(f"\n## Comment from {comment['memberCreator']['fullName']} on {comment['date'][:10]}\n")
        print(comment['data']['text'])


if __name__ == '__main__':
    main()
