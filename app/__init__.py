from celery import Celery, Task, current_app
from flask import Flask
from flask_restx import Api, Resource


BASE_URL = "/parser"


def celery_create_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask, broker="redis://127.0.0.1:6379", backend="redis://127.0.0.1:6379")
    # celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app


def get_celery_queue_items(queue_name):
    import base64
    import json  

    # Get a configured instance of a celery app:

    with current_app.pool.acquire(block=True) as conn:
        tasks = conn.default_channel.client.lrange(queue_name, 0, -1)
        decoded_tasks = []

    for task in tasks:
        print("KK task", task)
        j = json.loads(task)
        body = json.loads(base64.b64decode(j['body']))
        decoded_tasks.append(body)

    return decoded_tasks

def get_celery_all_tasks():
    from celery.app.control import inspect
    # Get a list of all task IDs
    i = inspect(app=current_app)
    task_ids = [task['id'] for tasks in i.active().values() for task in tasks]

    # Get the AsyncResult for each task ID
    from celery.result import AsyncResult
    results = [AsyncResult(task_id, app=current_app) for task_id in task_ids]

    # Get the state and result of each task
    tasks = []
    for result in results:
        tasks.append({
            'id': result.id,
            'state': result.state,
            'result': result.result
        })

    return tasks


def create_app():
    from app.routes import register_routes
    app = Flask(__name__, instance_relative_config=False)

    api = Api(
        app,
        title="Arborator-Grew Parser",
        version="0.1.0",
        doc=f"{BASE_URL}/doc",
        endpoint=f"{BASE_URL}/",
        base_url=f"{BASE_URL}/",
    )

    register_routes(api, BASE_URL)

    @api.route(f"{BASE_URL}/healthy")
    class Healthy(Resource):
        def get(self):
            return {"healthy": True}
        
    from celery.result import AsyncResult

    @api.route(f"{BASE_URL}/result/<id>")
    class Add(Resource):
        def get(self, id: str):
            print("KK id", id)
            result = AsyncResult(id)

            # print("KK get_celery_queue_items", get_celery_queue_items("myqueue"))
            # print("KK result", dir(result))
            r = {
                "ready": result.ready(),
                "successful": result.successful(),
                "value": result.result if result.ready() else None,
            }
            print("KK r", r)
            print("KK current_app.events", dir(current_app))
            i = current_app.control.inspect().active()
            task_ids = [task['id'] for tasks in i.values() for task in tasks]
            # Get the AsyncResult for each task ID
            results = [AsyncResult(task_id, app=app) for task_id in task_ids]

            # Get the state and result of each task
            tasks = []
            for result in results:
                tasks.append({
                    'id': result.id,
                    'state': result.state,
                    'result': result.result
                })
            print("KK tasks", tasks)
            # for task in current_app.events.State.tasks_by_timestamp():
            #     print("KK event", task)
            return r

    return app
