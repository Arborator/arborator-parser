import json
import os
import shutil
from pathlib import Path
from typing import Literal, TypedDict
from dotenv import load_dotenv



load_dotenv(dotenv_path=".flaskenv", verbose=True)

PATH_MODELS = os.getenv("PATH_MODELS") or "/home/arboratorgrew/models"
PATH_MODELS_QUICK_PARSER = os.getenv("PATH_MODELS_QUICK_PARSER") or "/home/arboratorgrew/parser_grew_models"
print(f"Models Folder : {PATH_MODELS}")
PATH_BERTFORDEPREL_VENV = os.getenv("PATH_BERTFORDEPREL_VENV") or "/home/arboratorgrew/arborator-parser/BertForDeprel/.venv/bin/python"

PATH_BERTFORDEPREL_SCRIPT = Path(__file__).parent.parent.parent / "BertForDeprel" / "BertForDeprel" / "run.py"


if not os.path.exists(PATH_MODELS):
    os.mkdir(PATH_MODELS)
elif not os.path.isdir(PATH_MODELS):
    raise SystemError(f"`PATH_MODELS` (=`{PATH_MODELS}`) already exists and is a file. Forbidden, crashing application.")

if not os.path.isfile(PATH_BERTFORDEPREL_SCRIPT):
    raise SystemError(f"No PATH_BERTFORDEPREL_SCRIPT=`{PATH_BERTFORDEPREL_SCRIPT}` file found")


class ModelInfo_t(TypedDict):
    project_name: str
    model_id: str


class ModelService:
    @staticmethod
    def available_models(models_path):
        if models_path is None: 
            print("PATH_MODELS", PATH_MODELS)
            models_path = PATH_MODELS
        
        project_names = os.listdir(models_path)
        model_info_list = []
        
        for project_name in project_names:
            path_project = os.path.join(models_path, project_name)
            
            try:
                models = os.listdir(path_project)
            except NotADirectoryError:
                continue
            
            for model_id in models:
                path_model = os.path.join(path_project, model_id)
                path_success_file = os.path.join(path_model, ".finished")
                path_best_epoch_scores = os.path.join(path_model, "scores.best.json")
                
                if os.path.isfile(path_success_file):
                    with open(path_best_epoch_scores) as infile:
                        scores_best_epoch = json.loads(infile.read())
                    
                    model_info = {
                        "model_id":  model_id,
                        "project_name": project_name,
                    }
                    model_info_list.append({
                        "model_info":  model_info,
                        "scores_best": scores_best_epoch
                    })
        
        print(f"|model_info_list| = {len(model_info_list)}")
        return model_info_list

    @staticmethod
    def available_models_quick_parser(models_path):
        model_info_list = []
        
        for item in os.listdir(models_path):
            item_path = os.path.join(models_path, item)
            
            if not os.path.isdir(item_path):
                continue
            
            path_best_epoch_scores = os.path.join(item_path, "scores.best.json")
            
            if os.path.isfile(path_best_epoch_scores):
                try:
                    with open(path_best_epoch_scores) as infile:
                        scores_best_epoch = json.loads(infile.read())
                    
                    model_info = {
                        "model_id": "",
                        "project_name": item,
                    }
                    model_info_list.append({
                        "model_info": model_info,
                        "scores_best": scores_best_epoch
                    })
                except Exception as e:
                    print(f"Error reading {path_best_epoch_scores}: {e}")
        
        print(f"|model_info_list| = {len(model_info_list)}")
        return model_info_list

        
    @staticmethod
    def make_model_folder_path_from_model_info(model_info:  ModelInfo_t):

        if not model_info.get("model_id"):
            quick_parser_path = os.path.join(PATH_MODELS_QUICK_PARSER, model_info["project_name"])
            if os.path.isdir(quick_parser_path):
                return quick_parser_path
            else:
                return os.path.join(PATH_MODELS, model_info["project_name"])

        prod_path = os.path.join(PATH_MODELS, model_info["project_name"], model_info["model_id"])
        if os.path.isdir(prod_path):
            return prod_path

        return prod_path


    @staticmethod
    def get_model_state(model_info:   ModelInfo_t) -> Literal["NO_EXIST", "TRAINING", "READY"]: 
        model_folder_path = ModelService.make_model_folder_path_from_model_info(model_info)
        if not os.path.isdir(model_folder_path):
            return "NO_EXIST"

        path_best_scores = os.path.join(model_folder_path, "scores.best.json")
        path_success_file = os.path.join(model_folder_path, ".finished")
        
        if os.path.isfile(path_best_scores) or os.path.isfile(path_success_file):
            return "READY"

        return "TRAINING"
    
    @staticmethod
    def remove_model(model_info: ModelInfo_t): 
        model_folder_path = ModelService.make_model_folder_path_from_model_info(model_info)
        try: 
            shutil.rmtree(model_folder_path, ignore_errors=False)
            return { "status": "success" }
        except Exception as e:
           return { "status": "failure", "error": "Error while removing pretrained model {}".format(str(e)) } 
            
            
