import json
import os
from pathlib import Path
from typing import Literal, TypedDict
from dotenv import load_dotenv


load_dotenv(dotenv_path=".flaskenv", verbose=True)

PATH_MODELS = os.getenv("PATH_MODELS") or "/home/arboratorgrew/models"
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
    def available_models():
        project_names = os.listdir(PATH_MODELS)
        model_info_list = []
        for project_name in project_names:
            path_project = os.path.join(PATH_MODELS, project_name)
            models = os.listdir(path_project)
            for model_id in models:
                path_model = os.path.join(path_project, model_id)
                path_success_file = os.path.join(path_model, ".finished")
                path_best_epoch_scores = os.path.join(path_model, "scores.best.json")

                if os.path.isfile(path_success_file):
                    with open(path_best_epoch_scores) as infile:
                        scores_best_epoch = json.loads(infile.read())
                    
                    model_info = {
                        "model_id": model_id,
                        "project_name": project_name,
                    }
                    model_info_list.append(
                        {
                            "model_info": model_info,
                            "scores_best": scores_best_epoch
                        }
                        )
        return model_info_list

    @staticmethod
    def make_model_folder_path_from_model_info(model_info: ModelInfo_t):
        model_folder_path = os.path.join(PATH_MODELS, model_info["project_name"], model_info["model_id"])
        return model_folder_path
    
    @staticmethod
    def get_model_state(model_info: ModelInfo_t) -> Literal["NO_EXIST", "TRAINING", "READY"]:
        model_folder_path = ModelService.make_model_folder_path_from_model_info(model_info)
        if not os.path.isdir(model_folder_path):
            return "NO_EXIST"
        path_success_file = os.path.join(model_folder_path, ".finished")
        if os.path.isfile(path_success_file):
            return "READY"
        return "TRAINING"

