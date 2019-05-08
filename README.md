# trello2md

A simple script to transform Trello card JSON to Markdown, currently tailored to my note-taking workflow.

## Usage

Install on your path with [pipx](https://github.com/pipxproject/pipx):

```
$ pipx install trello2md
```

Follow [Trello's instructions to download JSON for a card](https://help.trello.com/article/747-exporting-data-from-trello-1), then:

```
$ trello2md sample-card.json
# Sample Card

**Due:** 2019-05-07

Sample description

## Checklist

- [x] Completed item
- [ ] Incomplete item

## Attachments

- [Example link](https://example.com)

## Comment from Brian Rutledge on 2019-05-06

Sample comment

```
