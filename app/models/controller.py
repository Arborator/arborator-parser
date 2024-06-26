import json
import os
from typing import Dict, TypedDict, Union
from app.utils import get_readable_current_time_paris_ms

from flask import request
from flask_restx import Resource, Namespace
from flask_accepts.decorators.decorators import responds, accepts

from conllup.conllup import findConllFormatErrors

from .schema import ModelTrainStartPostSchema, ModelTrainStatusPostSchema, ModelParseStartPostSchema, ModelParseStatusPostSchema
from .service import ModelService
from .interface import ParsingSettings_t

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


@namespace.route("/list/<string:project_name>/<string:model_id>")
class ModelIdResource(Resource):
    def delete(self, project_name: str, model_id: str):
        model_info = {
            "project_name": project_name,
            "model_id": model_id
        }
        model_state = ModelService.get_model_state(model_info)
        if model_state == 'NO_EXIST': 
            return {
                "status": "failure",
                "error": "The model does not exist in the parser server"
            }
        else: 
            return ModelService.remove_model(model_info)
  
  
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
            model_folder_path = ModelService.make_model_folder_path_from_model_info(data["model_info"])
            path_history = os.path.join(model_folder_path, "scores.history.json")
            if os.path.isfile(path_history):
                with open(path_history, "r") as infile:
                    scores_history = json.loads(infile.read())
            else:
                scores_history = None

            path_best = os.path.join(model_folder_path, "scores.best.json")
            if os.path.isfile(path_history):
                with open(path_best, "r") as infile:
                    scores_best = json.loads(infile.read())
            else:
                scores_best = None
            return {"status": "success", "data": {"ready": False,
                                                    "scores_history": scores_history,
                                                    "scores_best": scores_best,
                                                  }}
        

class ModelParserStartPost_ED(TypedDict):
    project_name: str
    model_info: ModelInfo_t
    to_parse_samples: Dict[str, str]
    parsing_settings: ParsingSettings_t

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
        result = celery_tasks.parse_sentences.delay(model_info, data["to_parse_samples"], data["parsing_settings"])
        
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
        