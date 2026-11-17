import os

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
# Read the DB location from the environment so tests (and later Kubernetes)
# can point the app at a different database without changing code.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(20), default="Pending")

    def to_dict(self):
        """Single place that decides what a task looks like in JSON."""
        return {"id": self.id, "title": self.title, "description": self.description, "status": self.status}


# --- Input validation -------------------------------------------------------
# Limits come from the column definitions, so the model is the single source
# of truth. SQLite does NOT enforce String(n) lengths, so we must check here.
TITLE_MAX = Task.title.type.length
DESCRIPTION_MAX = Task.description.type.length
ALLOWED_STATUSES = {"Pending", "In Progress", "Completed"}


def validate_task(data, partial):
    """Check a request body. Returns (clean_fields, None) or (None, error_message).

    partial=False (create): title is required.
    partial=True  (update): only the fields present are checked; status may be set.
    """
    if not isinstance(data, dict):
        return None, "Request body must be a JSON object"

    clean = {}

    if not partial or "title" in data:
        title = data.get("title")
        # isinstance(..., str) rejects None, numbers, lists and booleans in one go
        if not isinstance(title, str) or not title.strip():
            return None, "'title' is required and must be a non-empty string"
        title = title.strip()
        if len(title) > TITLE_MAX:
            return None, f"'title' must be at most {TITLE_MAX} characters"
        clean["title"] = title

    if "description" in data:
        description = data["description"]
        if not isinstance(description, str):
            return None, "'description' must be a string"
        if len(description) > DESCRIPTION_MAX:
            return None, f"'description' must be at most {DESCRIPTION_MAX} characters"
        clean["description"] = description

    if partial and "status" in data:
        status = data["status"]
        if status not in ALLOWED_STATUSES:
            return None, f"'status' must be one of: {', '.join(sorted(ALLOWED_STATUSES))}"
        clean["status"] = status

    return clean, None


# Initialize database
with app.app_context():
    db.create_all()


@app.route('/tasks', methods=['POST'])
def create_task():
    # silent=True: invalid JSON gives None instead of raising -> validator rejects it
    fields, error = validate_task(request.get_json(silent=True), partial=False)
    if error:
        return jsonify({"error": error}), 400
    new_task = Task(title=fields["title"], description=fields.get("description", ""), status="Pending")
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"message": "Task created!", "id": new_task.id}), 201


@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([t.to_dict() for t in tasks])


@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task.to_dict())


@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    fields, error = validate_task(request.get_json(silent=True), partial=True)
    if error:
        return jsonify({"error": error}), 400
    # Validate everything first, then change the task: a bad request never
    # leaves it half-updated.
    for name, value in fields.items():
        setattr(task, name, value)
    db.session.commit()
    return jsonify({"message": "Task updated!"})


@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted!"})


@app.route('/')
def home():
    return "Task Tracker API up"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
