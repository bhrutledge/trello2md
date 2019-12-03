"""Allow execution via `python -m trello2md ...`."""
import sys

from .cli import main

sys.exit(main())
