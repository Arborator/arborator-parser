import time
from typing import Dict, List, TypedDict, Union
from app.utils import get_readable_current_time_paris_ms

from flask import request
from flask_restx import Api, Resource, Namespace
from flask_accepts.decorators.decorators import responds, accepts

from .schema import ModelTrainStartPostSchema, ModelTrainStatusPostSchema, ModelParseStartPostSchema, ModelParseStatusPostSchema
from .service import ModelService

from . import celery_tasks


class ModelInfo_t(TypedDict):
    project_name: str
    model_id: str

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
    base_model: Union[None, ModelInfo_t]

@namespace.route("/train/start")
class ModelTrainerResource(Resource):
    "Model Trainer"
    @accepts(schema=ModelTrainStartPostSchema, api=namespace)
    def post(self):
        data: ModelTrainerPost_ED = request.parsed_obj
        
        model_info = {
            "project_name": data["project_name"],
            "model_id": get_readable_current_time_paris_ms(),
        }

        model_state = ModelService.get_model_state(model_info) 
        if model_state != "NO_EXIST":
            return {
                "status": "failure",
                "error": "Model that you want to create already exist with same ID",
            }
        
        if data["base_model"]:
            base_model_state = ModelService.get_model_state(data["base_model"]) 
            if base_model_state != "READY":
                return {
                    "status": "failure",
                    "error": "Base Model doesn't exist",
                }
        result = celery_tasks.train_model.delay(model_info, data["train_samples"], data["max_epoch"], data["base_model"])
        
        return {
            "status": "success",
            "data": {
                "model_info": model_info,
                "train_task_id": result.id,
            }
        }



class ModelTrainStatus_ED(TypedDict):
    model_info: ModelInfo_t
    train_task_id: str


@namespace.route("/train/status")
class ModelTrainStatusResource(Resource):
    @accepts(schema=ModelTrainStatusPostSchema, api=namespace)
    def post(self):
        data: ModelTrainStatus_ED = request.parsed_obj
        train_task_id = data["train_task_id"]
        result = AsyncResult(train_task_id)
        if result.ready():
            if result.successful():
                return result.result
            else:
                {"status": "failure", "error": "Task resulted in a failure"}
        else:
            return {"status": "success", "data": {"ready": False}}
        

class ModelParserStartPost_ED(TypedDict):
    project_name: str
    model_info: ModelInfo_t
    to_parse_samples: Dict[str, str]

@namespace.route("/parse/start")
class ModelParserStartResource(Resource):
    "Model Parser"
    @accepts(schema=ModelParseStartPostSchema, api=namespace)
    def post(self):
        data: ModelParserStartPost_ED = request.parsed_obj
        
        model_info = data["model_info"]

        model_state = ModelService.get_model_state(model_info) 
        if model_state != "READY":
            return {
                "status": "failure",
                "error": "Model not ready yet",
            }
        print("KK before CELERY")
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
    @accepts(schema=ModelParseStatusPostSchema, api=namespace)
    def post(self) -> Dict[str, object]:
        data: ModelParserStatusPost_ED = request.parsed_obj
        parse_task_id = data["parse_task_id"]
        result = AsyncResult(parse_task_id)
        if result.ready():
            if result.successful():
                return result.result
            else:
                {"status": "failure", "error": "Task resulted in a failure"}
        else:
            return {"status": "success", "data": {"ready": False}}
        