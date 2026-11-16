import os

import pytest

# Must be set BEFORE importing app, because app.py reads it at import time.
# An in-memory SQLite DB means tests never touch your real database.db.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import app as flask_app, db  # noqa: E402


@pytest.fixture
def client():
    """A test client with a fresh, empty database for every test."""
    flask_app.config["TESTING"] = True
    with flask_app.app_context():
        db.drop_all()
        db.create_all()
    with flask_app.test_client() as client:
        # `return` would end this function (and close the `with` block) before
        # the test runs. `yield` instead pauses here and hands `client` to the
        # test; pytest resumes the function after the test so cleanup can run.
        yield client
