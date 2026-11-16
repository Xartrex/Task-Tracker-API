# Task-Tracker-API
[![CI](https://github.com/Xartrex/Task-Tracker-API/actions/workflows/ci.yml/badge.svg)](https://github.com/Xartrex/Task-Tracker-API/actions/workflows/ci.yml)

Basic Python API testing covering backend, database, and API development

The API has 4 methods (HTTP Requests): GET, POST, PUT, DELETE

It can be executed by typying:

```bash
python app.py
```

The app can be tested with the following curls:
```bash
curl -X POST http://127.0.0.1:5000/tasks -H "Content-Type: application/json" -d '{"title": "Buy groceries", "description": "Milk, Eggs, Bread"}'
curl -X GET http://127.0.0.1:5000/tasks
curl -X PUT http://127.0.0.1:5000/tasks/1 -H "Content-Type: application/json" -d '{"status": "Completed"}'
curl -X GET http://127.0.0.1:5000/tasks
curl -X DELETE http://127.0.0.1:5000/tasks/1
curl -X GET http://127.0.0.1:5000/tasks
```


## Testing
Tests live in `tests/` and use **pytest** with Flask's built-in test client, so no server needs to be running.

```bash
python -m venv myvenv && source myvenv/bin/activate
pip install -r requirements-dev.txt   # app deps + pytest + ruff
ruff check .                          # lint: catches unused imports, typos, style issues
pytest -v                             # run the test suite
```

Key ideas:
- `tests/conftest.py` sets `DATABASE_URL=sqlite:///:memory:` **before** importing the app, so tests use a throwaway in-memory database instead of `database.db`.
- The `client` fixture drops and recreates the tables before every test, so tests are independent of each other.
- `requirements-dev.txt` holds tools needed only for development/CI, keeping the production image small. `.dockerignore` keeps tests, the venv and local DB files out of the image.


## CI (Continuous Integration) with GitHub Actions
CI means every change is checked automatically before it is trusted. The pipeline lives in `.github/workflows/ci.yml` and GitHub runs it on every push to `main`, on every pull request, or manually from the **Actions** tab ("Run workflow").

Vocabulary:

| Term | Meaning |
| ---- | ------- |
| Workflow | A YAML file in `.github/workflows/`; one automated process |
| Trigger (`on:`) | The event that starts it (push, pull_request, manual...) |
| Job | A group of steps running on its own fresh VM (a *runner*). Jobs run in parallel unless `needs:` says otherwise |
| Step | One command (`run:`) or a reusable action (`uses:`), executed in order |
| Action | A packaged step someone published, e.g. `actions/checkout` downloads the repo |

Our pipeline:
```
push / PR
   │
   ▼
[ test ]  checkout → setup Python 3.12 → pip install → ruff check → pytest
   │ (only if green: needs: test)
   ▼
[ docker ] checkout → docker build → run container → curl / (smoke test)
```
If any step fails, the run turns red ❌, later steps are skipped and GitHub shows the error log. The badge at the top of this README shows the status of the latest run on `main`.

## Docker
In order to create a docker container for the app, a Dockerfile must be created, specifying:
- Python version
- Working directory withing the container (i.e /app), so data can be copied inside
- How python dependencies are installed (i.e python install -r requirements.txt)
- Port in which the app will be exposed, and therefore accessed
- Command to be executed by the container: CMD ["python", "app.py"]

After the creation of the Dockerfile, the image of the container must be build before it can be deployed:
```bash
docker-buildx build -t task-tracker .
```

Finally, the built image can be deployed:
```bash
docker run -p 5000:5000 task-tracker
```

## Mini Kubernetes (k8s)
🚀 Kubernetes & Kubernetes Clusters Explained
🔹 What is Kubernetes?

Kubernetes (K8s) is an open-source container orchestration platform that automates:
✅ Deployment of applications
✅ Scaling apps up or down
✅ Load balancing between multiple instances
✅ Self-healing (restarts failed containers)

Originally developed by Google, Kubernetes is now the industry standard for managing containerized applications.

🔹 Why Use Kubernetes?

    Before Kubernetes: You had to manually start, stop, and manage multiple Docker containers.
    With Kubernetes: It automates everything—managing containers, scaling apps, and handling failures.

 What is a Kubernetes Cluster?

A Kubernetes cluster is a group of machines (physical or virtual) that run Kubernetes-managed applications.

A cluster is made up of:

| Component    | Description                                                               |
| ------------ | ------------------------------------------------------------------------- |
| Master Node  | The brain of Kubernetes; manages the cluster                              |
| Worker Nodes | The machines where containers (Pods) run                                  |
| Pods         | The smallest unit in Kubernetes, containing one or more Docker containers |

When you deploy an app, Kubernetes does the following:
1. Schedules it on a Worker Node
2. Creates a Pod that runs your app’s container
3. Manages networking & load balancing
4. Monitors & restarts containers if they fail
5. Scales up/down based on demand

🔹 Example Cluster Setup
```scss
                Kubernetes Cluster
        ┌────────────────────────────┐
        │        Master Node         │
        │ ───────────────────────── │
        │  - API Server              │
        │  - Scheduler               │
        │  - Controller Manager      │
        │  - etcd (Database)         │
        └────────────────────────────┘
                        │
        ┌────────────────────────────────┐
        │          Worker Nodes          │
        │ ───────────────────────────── │
        │ Pod 1  → [ App Container ]     │
        │ Pod 2  → [ App Container ]     │
        │ Pod 3  → [ App Container ]     │
        └────────────────────────────────┘
```

🔥Summary

| Concept      | What It Does                                                  |
| ------------ | ------------------------------------------------------------- |
| Kubernetes   | Manages & automates containerized applications                |
| Cluster      | A group of machines running Kubernetes                        |
| Master Node  | Controls & manages the cluster                                |
| Worker Nodes | Run your app inside Pods                                      |
| Pods         | The smallest unit in Kubernetes, containing Docker containers |

