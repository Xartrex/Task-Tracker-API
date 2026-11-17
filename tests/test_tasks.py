def create(client, **fields):
    return client.post("/tasks", json=fields)


def test_home(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Task Tracker API up" in resp.data


def test_list_starts_empty(client):
    assert client.get("/tasks").get_json() == []


def test_create_task(client):
    # Asserts run top to bottom and the test stops at the first one that fails
    # (AssertionError exits the function), so later code never runs. The test
    # passes only if every assert passes. The basic check (was the task created?)
    # goes first, so a failure points to the earliest thing that went wrong.
    resp = create(client, title="Buy groceries", description="Milk, Eggs")
    assert resp.status_code == 201

    tasks = client.get("/tasks").get_json()
    assert tasks == [
        {"id": 1, "title": "Buy groceries", "description": "Milk, Eggs", "status": "Pending"}
    ]


def test_create_task_without_title_is_rejected(client):
    resp = create(client, description="no title here")
    assert resp.status_code == 400
    assert client.get("/tasks").get_json() == []


def test_get_task_by_id(client):
    task_id = create(client, title="Read docs", description="Flask routing").get_json()["id"]

    resp = client.get(f"/tasks/{task_id}")
    assert resp.status_code == 200
    assert resp.get_json() == {
        "id": task_id, "title": "Read docs", "description": "Flask routing", "status": "Pending"
    }


def test_get_missing_task_returns_404(client):
    resp = client.get("/tasks/999")
    assert resp.status_code == 404
    assert "error" in resp.get_json()


def test_single_and_list_endpoints_use_same_shape(client):
    # Guards the shared serializer (to_dict): if someone adds a field to one
    # endpoint and forgets the other, this fails.
    task_id = create(client, title="Same shape").get_json()["id"]
    assert client.get(f"/tasks/{task_id}").get_json() == client.get("/tasks").get_json()[0]


def test_update_task(client):
    task_id = create(client, title="Write tests").get_json()["id"]

    resp = client.put(f"/tasks/{task_id}", json={"status": "Completed"})
    assert resp.status_code == 200

    task = client.get("/tasks").get_json()[0]
    assert task["status"] == "Completed"
    assert task["title"] == "Write tests"  # untouched fields are kept


def test_update_missing_task_returns_404(client):
    assert client.put("/tasks/999", json={"status": "Completed"}).status_code == 404


def test_delete_task(client):
    task_id = create(client, title="Temporary").get_json()["id"]

    assert client.delete(f"/tasks/{task_id}").status_code == 200
    assert client.get("/tasks").get_json() == []


def test_delete_missing_task_returns_404(client):
    assert client.delete("/tasks/999").status_code == 404
