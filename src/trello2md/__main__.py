"""Allow execution via `python -m trello2md ...`."""
import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
