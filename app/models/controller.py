from flask_accepts.decorators.decorators import responds
from flask_restx import Api, Resource, Namespace
from .schema import ModelSchema


namespace = Namespace("models", description="Create, Access, List and Delete Models")


@namespace.route("/")
class ModelsResource(Resource):
    "Models"
    @responds(schema=ModelSchema(many=True), api=namespace)
    def get(self):
        return []

