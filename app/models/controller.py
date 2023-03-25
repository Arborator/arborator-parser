import time
from typing import Dict, List, TypedDict

from flask import request
from flask_restx import Api, Resource, Namespace
from flask_accepts.decorators.decorators import responds, accepts

from .schema import ModelTrainerPostSchema, ModelParserPostSchema
from .service import ModelService

from . import celery_tasks


namespace = Namespace("models", description="Create, Access, List and Delete Models")


@namespace.route("/")
class ModelsResource(Resource):
    "Models"
    # @responds(schema=ModelSchema(many=True), api=namespace)
    def get(self):
        return ModelService.available_models()


# ED = Expected Definition
class ModelTrainerPost_ED(TypedDict):
    project_name: str
    train_samples: Dict[str, str]
    max_epoch: int

@namespace.route("/train")
class ModelTrainerResource(Resource):
    "Model Trainer"
    @accepts(schema=ModelTrainerPostSchema, api=namespace)
    def post(self):
        data: ModelTrainerPost_ED = request.parsed_obj
        
        model_info = {
            "project_name": data["project_name"],
            "model_id": str(int(time.time())),
            "max_epoch": data["max_epoch"],
        }

        print("KK model_info", model_info)
        result = celery_tasks.train_model.delay(model_info, data["train_samples"])
        
        return {
            "model_info": model_info,
            "task_id": result.id,
        }


class ModelParserPost_ED(TypedDict):
    project_name: str
    model_id: str
    to_parse_samples: Dict[str, str]


@namespace.route("/parse")
class ModelTrainerResource(Resource):
    "Model Trainer"
    @accepts(schema=ModelParserPostSchema, api=namespace)
    def post(self):
        data: ModelParserPost_ED = request.parsed_obj
        
        model_info = {
            "project_name": data["project_name"],
            "model_id": data["model_id"],
        }

        result = celery_tasks.parse_sentences(model_info, data["to_parse_samples"])
        
        return {
            "model_info": model_info,
            "parsed_conlls": result,
        }