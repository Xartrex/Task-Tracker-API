"""Input validation at the API boundary (issue #3).

Rules under test:
- title:       string, 1-100 chars after trimming whitespace, required on create
- description: string, max 200 chars, optional
- status:      one of ALLOWED_STATUSES (only settable via PUT)
- body:        must be a JSON object; anything else -> 400

Every rejected request must return 400 with an {"error": ...} body that names
the offending field, and must leave the database unchanged.

The limits mirror the DB columns in app.py (String(100), String(200)).
"""
import pytest

ALLOWED_STATUSES = ["Pending", "In Progress", "Completed"]


def create(client, **fields):
    return client.post("/tasks", json=fields)


def assert_rejected(resp, field=None):
    assert resp.status_code == 400, resp.get_data(as_text=True)
    body = resp.get_json()
    assert "error" in body
    if field:
        assert field in body["error"]


# --- POST /tasks -----------------------------------------------------------

# parametrize = run the same test once per tuple; pytest reports each case
# separately, so you see exactly which input broke.
@pytest.mark.parametrize("payload, field", [
    ({"title": ""}, "title"),
    ({"title": "   "}, "title"),                   # whitespace only
    ({"title": None}, "title"),
    ({"title": 123}, "title"),                     # wrong type
    ({"title": ["a", "b"]}, "title"),
    ({"title": "x" * 101}, "title"),               # one over the limit
    ({"title": "ok", "description": 42}, "description"),
    ({"title": "ok", "description": "x" * 201}, "description"),
], ids=["empty", "whitespace", "null", "int", "list", "too-long", "desc-int", "desc-too-long"])
def test_create_rejects_invalid_fields(client, payload, field):
    assert_rejected(client.post("/tasks", json=payload), field)
    assert client.get("/tasks").get_json() == []   # nothing was saved


def test_create_accepts_values_at_the_limits(client):
    # Boundary test: the max length itself must be allowed (off-by-one check).
    resp = create(client, title="x" * 100, description="y" * 200)
    assert resp.status_code == 201


@pytest.mark.parametrize("body", [
    "[1, 2, 3]",          # valid JSON, but a list, not an object
    '"just a string"',
    "not json at all",
], ids=["list", "string", "not-json"])
def test_create_rejects_non_object_body(client, body):
    resp = client.post("/tasks", data=body, content_type="application/json")
    assert_rejected(resp)


# --- PUT /tasks/<id> -------------------------------------------------------

@pytest.mark.parametrize("payload, field", [
    ({"title": ""}, "title"),
    ({"title": None}, "title"),                    # would violate NOT NULL
    ({"title": 123}, "title"),
    ({"title": "x" * 101}, "title"),
    ({"description": 42}, "description"),
    ({"description": "x" * 201}, "description"),
    ({"status": "Hacked"}, "status"),              # not an allowed value
    ({"status": "completed"}, "status"),           # case matters
    ({"status": None}, "status"),
], ids=["empty", "null", "int", "too-long", "desc-int", "desc-too-long", "unknown-status", "wrong-case-status", "null-status"])
def test_update_rejects_invalid_fields(client, payload, field):
    task_id = create(client, title="Original").get_json()["id"]

    assert_rejected(client.put(f"/tasks/{task_id}", json=payload), field)

    task = client.get(f"/tasks/{task_id}").get_json()
    assert task["title"] == "Original"             # unchanged
    assert task["status"] == "Pending"


@pytest.mark.parametrize("status", ALLOWED_STATUSES)
def test_update_accepts_every_allowed_status(client, status):
    task_id = create(client, title="Move me").get_json()["id"]
    assert client.put(f"/tasks/{task_id}", json={"status": status}).status_code == 200
    assert client.get(f"/tasks/{task_id}").get_json()["status"] == status


def test_update_rejects_non_object_body(client):
    task_id = create(client, title="Original").get_json()["id"]
    resp = client.put(f"/tasks/{task_id}", data="[1]", content_type="application/json")
    assert_rejected(resp)
