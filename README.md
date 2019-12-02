# trello2md

Export Trello boards and cards to Markdown. Currently tailored to my note-taking workflow.

## Installation

Install on your path with [pipx](https://github.com/pipxproject/pipx):

```
$ pipx install trello2md
```

Authorize use of the Trello API:

```
$ trello2md auth
```

## Exporting a Trello board

Run with the URL for a Trello board as the only argument to write Markdown files to a directory. For example:

```
$ trello2md https://trello.com/b/WODq2cwg/sample-board

$ tree sample-board/
sample-board/
├── another-card-1.md
├── another-card-2.md
├── another-card.md
├── copied-card.md
├── index.md
└── sample-card.md

$ cat sample-board/index.md
# {Sample Board}

## Sample List

- [Sample Card](sample-card.md)
- [Copied Card](copied-card.md)

## Empty List

## Another List

- [Another Card](another-card.md)
- [Another Card](another-card-1.md)
- [Another Card](another-card-2.md)
```

## Exporting a Trello card

Run with the URL for a Trello card as the only argument to print Markdown. For example:

```
$ trello2md https://trello.com/c/HGYGb5iM/2-sample-card
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

## Developing

- [Fork and clone](https://help.github.com/en/articles/fork-a-repo) this repository

- Create and activate a [virtual environment](https://docs.python.org/3/tutorial/venv.html)

    ```
    $ cd trello2md

    $ python3 -m venv venv

    $ source venv/bin/activate
    ```

- Install this package and its dependencies for development

    ```
    $ pip install -e .[dev]
    ```

    This will install:

    - [pytest](https://docs.pytest.org/en/latest/) for writing and running tests
    - [mypy](https://mypy.readthedocs.io/en/latest/) to check types
    - [black](https://black.readthedocs.io/en/stable/) to format the code
    - [flake8](http://flake8.pycqa.org/en/latest/) to identify coding errors and check code style
    - [pydocstyle](http://www.pydocstyle.org/en/latest/) to check docstring style
