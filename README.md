# Task-Tracker-API
Basic Python API testing covering backend, database, and API development

The API has 4 methods (HTTP Requests): GET, POTS, PUT, DELETE

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


