import sys
from io import StringIO

from trello2md import api


def test_get_credentials(monkeypatch):
    inputs = StringIO(
        # Enter your API key:
        "api_key\n"
        # Enter your API secret:
        "api_secret\n"
    )
    monkeypatch.setattr(sys, "stdin", inputs)

    def stub_create_token(**kwargs):
        assert kwargs == {
            "expiration": "never",
            "scope": "read",
            "key": "api_key",
            "secret": "api_secret",
            "name": "trello2md",
            "output": False,
        }
        return {"oauth_token": "oauth_token"}

    monkeypatch.setattr(api.trello.util, "create_oauth_token", stub_create_token)

    credentials = api.get_credentials("trello2md")

    assert credentials == {"api_key": "api_key", "token": "oauth_token"}
