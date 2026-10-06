from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    completed = db.Column(db.Boolean, default=False)
    def to_dict(self):
        return {"id": self.id, "title": self.title, "description": self.description, "completed": self.completed}
API_KEY = "mymodule5key123"
def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get('x-api-key')
        if key != API_KEY:
            return jsonify({"status": "error", "message": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated
@app.route('/')
def home():
    return jsonify({"message": "Module 5 API Running"})
@app.route('/api/tasks', methods=['GET'])
@require_api_key
def get_tasks():
    tasks = Task.query.all()
    return jsonify([task.to_dict() for task in tasks])
@app.route('/api/tasks', methods=['POST'])
@require_api_key
def create_task():
    data = request.get_json()
    new_task = Task(title=data['title'], description=data.get('description',''), completed=data.get('completed', False))
    db.session.add(new_task)
    db.session.commit()
    return jsonify(new_task.to_dict()), 201
@app.route('/api/tasks/<int:task_id>', methods=['GET','PUT','DELETE'])
@require_api_key
def handle_task(task_id):
    task = Task.query.get_or_404(task_id)
    if request.method == 'GET':
        return jsonify(task.to_dict())
    elif request.method == 'PUT':
        data = request.get_json()
        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.completed = data.get('completed', task.completed)
        db.session.commit()
        return jsonify(task.to_dict())
    else:
        db.session.delete(task)
        db.session.commit()
        return jsonify({"message": "Task deleted"})
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
