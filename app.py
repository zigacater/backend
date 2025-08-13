import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Task
from schemas import task_schema, tasks_schema
from marshmallow import ValidationError

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SQLITE = f"sqlite:///{os.path.join(BASE_DIR, 'db.sqlite3')}"
DATABASE_URL = os.environ.get("DATABASE_URL", DEFAULT_SQLITE)

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    CORS(app)  # dovoli dostop iz frontenda
    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.route('/tasks', methods=['GET'])
    def get_tasks():
        # Iskanje in sortiranje
        q = request.args.get('q', type=str)
        sort = request.args.get('sort', default='priority')  
        order = request.args.get('order', default='desc')    

        query = Task.query
        if q:
            like = f"%{q}%"
            query = query.filter(
                (Task.title.ilike(like)) |
                (Task.description.ilike(like))
            )

        if sort == 'created_at':
            sort_col = Task.created_at
        else:
            sort_col = Task.priority

        if order == 'asc':
            query = query.order_by(sort_col.asc())
        else:
            query = query.order_by(sort_col.desc())

        tasks = query.all()
        return jsonify(tasks_schema.dump(tasks)), 200

    @app.route('/tasks/<int:task_id>', methods=['GET'])
    def get_task(task_id):
        task = Task.query.get_or_404(task_id)
        return jsonify(task_schema.dump(task)), 200

    @app.route('/tasks', methods=['POST'])
    def create_task():
        json_data = request.get_json() or {}
        try:
            data = task_schema.load(json_data)
        except ValidationError as err:
            return jsonify({'errors': err.messages}), 400

        task = Task(
            title=data.get('title'),
            description=data.get('description'),
            due_date=data.get('due_date'),
            priority=data.get('priority', 0)
        )
        db.session.add(task)
        db.session.commit()
        return jsonify(task_schema.dump(task)), 201

    @app.route('/tasks/<int:task_id>', methods=['PUT'])
    def update_task(task_id):
        task = Task.query.get_or_404(task_id)
        json_data = request.get_json() or {}
        try:
            data = task_schema.load(json_data, partial=True)
        except ValidationError as err:
            return jsonify({'errors': err.messages}), 400

        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'due_date' in data:
            task.due_date = data['due_date']
        if 'priority' in data:
            task.priority = data['priority']

        db.session.commit()
        return jsonify(task_schema.dump(task)), 200

    @app.route('/tasks/<int:task_id>', methods=['DELETE'])
    def delete_task(task_id):
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'deleted'}), 200

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5050, host='0.0.0.0')
