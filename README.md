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

    - [mypy](https://mypy.readthedocs.io/en/latest/) to check types
    - [black](https://black.readthedocs.io/en/stable/) to format the code
    - [flake8](http://flake8.pycqa.org/en/latest/) to identify coding errors and check code style
    - [pydocstyle](http://www.pydocstyle.org/en/latest/) to check docstring style
