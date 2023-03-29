import time
from typing import Dict, List, TypedDict

from flask import request
from flask_restx import Api, Resource, Namespace
from flask_accepts.decorators.decorators import responds, accepts

from .schema import ModelTrainStatusPostSchema, ModelTrainerPostSchema, ModelParserStartPostSchema
from .service import ModelService

from . import celery_tasks


namespace = Namespace("models", description="Create, Access, List and Delete Models")


@namespace.route("/list")
class ModelsResource(Resource):
    "Models"
    # @responds(schema=ModelSchema(many=True), api=namespace)
    def get(self):
        return {"status": "success", "data": ModelService.available_models()}


# ED = Expected Definition
class ModelTrainerPost_ED(TypedDict):
    project_name: str
    train_samples: Dict[str, str]
    max_epoch: int

@namespace.route("/train/start")
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

        model_state = ModelService.get_model_state(model_info) 
        if model_state != "NO_EXIST":
            return {
                "status": "failure",
                "error": "Model already exist with same ID",
            }

        print("KK model_info", model_info)
        result = celery_tasks.train_model.delay(model_info, data["train_samples"])
        
        return {
            "status": "success",
            "data": {
                "model_info": model_info,
                "task_id": result.id,
            }
        }



class ModelTrainStatus_ED(TypedDict):
    project_name: str
    model_id: str


@namespace.route("/train/status")
class ModelTrainStatusResource(Resource):
    @accepts(schema=ModelTrainStatusPostSchema, api=namespace)
    def post(self):
        data: ModelTrainStatus_ED = request.parsed_obj

        model_info = {
            "project_name": data["project_name"],
            "model_id": data["model_id"],
        }

        model_state = ModelService.get_model_state(model_info)
        return {
            "status": "success",
            "data": {
                "model_info": model_info,
                "task_status": model_state,
            }
        }


class ModelParserStartPost_ED(TypedDict):
    project_name: str
    model_id: str
    to_parse_samples: Dict[str, str]

@namespace.route("/parse/start")
class ModelParserStartResource(Resource):
    "Model Parser"
    @accepts(schema=ModelParserStartPostSchema, api=namespace)
    def post(self):
        data: ModelParserStartPost_ED = request.parsed_obj
        
        model_info = {
            "project_name": data["project_name"],
            "model_id": data["model_id"],
        }

        model_state = ModelService.get_model_state(model_info) 
        if model_state != "READY":
            return {
                "status": "failure",
                "error": "Model not ready yet",
            }

        result = celery_tasks.parse_sentences.delay(model_info, data["to_parse_samples"])
        
        return {
            "status": "success",
            "data": {
                "model_info": model_info,
                "parse_task_id": result.id,
            }
        }
    

from celery.result import AsyncResult


class ModelParserStatusPost_ED(TypedDict):
    parse_task_id: str

@namespace.route("/parse/status")
class ModelParserStatusResource(Resource):
    def post(self) -> Dict[str, object]:
        data: ModelParserStatusPost_ED = request.get_json(force=True)
        parse_task_id = data["parse_task_id"]
        result = AsyncResult(parse_task_id)
        status = "NO_EXIST"
        if result.ready():
            if result.successful():
                status = "READY"
            else:
                status = "FAILED"
        else:
            status = "PENDING"
        
        return {
            "status": "success",
            "data": {
                "task_status": status,
                "ready": result.ready(),
                "successful": result.successful(),
                "failed": result.failed(),
                "result": result.result if result.ready() else None,
            }
        }