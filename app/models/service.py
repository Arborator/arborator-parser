import json
import os
import shutil
import time
from pathlib import Path
from typing import Dict, List, Literal, TypedDict
from dotenv import load_dotenv
from celery import shared_task


load_dotenv(dotenv_path=".flaskenv", verbose=True)

PATH_MODELS = os.getenv("PATH_MODELS") or "/home/arboratorgrew/models"
PATH_BERTFORDEPREL_VENV = os.getenv("PATH_BERTFORDEPREL_VENV") or "/home/arboratorgrew/miniconda3/envs/kirian/bin/python3"

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
        return os.listdir(PATH_MODELS)

    @staticmethod
    def make_root_folder_path_from_model_info(model_info: ModelInfo_t):
        root_folder_path = os.path.join(PATH_MODELS, model_info["project_name"], model_info["model_id"])
        return root_folder_path
    
    @staticmethod
    def get_model_state(model_info: ModelInfo_t) -> Literal["NO_EXIST", "TRAINING", "READY"]:
        root_folder_path = ModelService.make_root_folder_path_from_model_info(model_info)
        if not os.path.isdir(root_folder_path):
            return "NO_EXIST"
        path_success_file = os.path.join(root_folder_path, "training_task_state.json")
        if os.path.isfile(path_success_file):
            return "READY"
        return "TRAINING"

