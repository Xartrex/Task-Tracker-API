# Task-Tracker-API
Basic Python API testing covering backend, database, and API development

The API has 4 methods (HTTP Requests): GET, PUT, PUT, DELETE

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

## Docker
In order to create a docker container for the app, a Dockerfile must be created, specifying:
- Python version
- Working directory withing the container (i.e /app), so data can be copied inside
- How python dependencies are installed (i.e python install -r requirements.txt)
- Port in which the app will be exposed, and therefore accessed
- Command to be executed by the container: CMD ["python", "app.py"]

After the creation of the Dockerfile, teh image of the container must be build before it can be deployed:
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

