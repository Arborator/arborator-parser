import json
import os
import shutil
import time
from typing import Dict, List, Union
from celery import shared_task
from .service import ModelInfo_t, ModelService, PATH_BERTFORDEPREL_VENV, PATH_BERTFORDEPREL_SCRIPT

DEFAULT_BASE_MODEL_CONFIG_PATH = "/models/SUD_all_1/config.json"

@shared_task()
def train_model(model_info: Dict[str, str], train_samples: Dict[str, str], max_epoch: int, base_model: Union[None, ModelInfo_t]):
    model_folder_path = ModelService.make_model_folder_path_from_model_info(model_info)
    if os.path.isdir(model_folder_path):
        return {"status": "failure", "error": "model already exist"}

    os.makedirs(model_folder_path)

    train_files_folder_path = os.path.join(model_folder_path, "train_conlls")
    os.makedirs(train_files_folder_path, exist_ok=True)

    for sample_name, sample_content in train_samples.items():
        sample_path = os.path.join(train_files_folder_path, sample_name + ".conllu")
        with open(sample_path, "w") as outfile:
            outfile.write(sample_content)

    if base_model:
        base_model_folder_path = ModelService.make_model_folder_path_from_model_info(base_model)
        base_model_config = os.path.join(base_model_folder_path, "config.json")
    else:
        base_model_config = DEFAULT_BASE_MODEL_CONFIG_PATH

    os.system(f"{PATH_BERTFORDEPREL_VENV} {PATH_BERTFORDEPREL_SCRIPT} train \
    --model_folder_path \"{model_folder_path}\" \
    --ftrain \"{train_files_folder_path}\" \
    --batch_size 16 \
    --gpu_ids 0 \
    --conf_pretrain {base_model_config} \
    --overwrite_pretrain_classifiers \
    --max_epoch {max_epoch}") 

    path_success_file = os.path.join(model_folder_path, ".finished")
    if not os.path.isfile(path_success_file):
        error_message = f"BertForDeprel/run.py didn't finish training model correctly. Search ERROR_101 in celery logs"
        print(error_message)
        shutil.rmtree(model_folder_path)
        return {"status": "failure", "error": error_message}

    path_history = os.path.join(model_folder_path, "scores.history.json")
    with open(path_history, "r") as infile:
        scores_history = json.loads(infile.read())

    path_best = os.path.join(model_folder_path, "scores.best.json")
    with open(path_best, "r") as infile:
        scores_best = json.loads(infile.read())

    return {"status": "success", "data": {
        "ready": True,
        "model_info": model_info,
        "scores_history": scores_history,
        "scores_best": scores_best,
    }}



@shared_task()
def parse_sentences(model_info: Dict[str, str], to_parse_samples: Dict[str, str]) -> bool:
    model_folder_path = ModelService.make_model_folder_path_from_model_info(model_info)

    model_config_path = os.path.join(model_folder_path, "config.json")

    time_now_str = str(int(time.time()))
    
    path_tmp = os.path.join(model_folder_path, time_now_str)

    inpath = os.path.join(path_tmp, "to_predict")
    outpath = os.path.join(path_tmp, "predicted")

    os.makedirs(inpath, exist_ok=True)
    os.makedirs(outpath, exist_ok=True)

    for conll_name, conll_content in to_parse_samples.items():
        path_to_write_conll = os.path.join(inpath, conll_name + ".conllu")
        with open(path_to_write_conll, "w") as outfile:
            outfile.write(conll_content)

    os.system(f"{PATH_BERTFORDEPREL_VENV} {PATH_BERTFORDEPREL_SCRIPT} predict \
    --conf \"{model_config_path}\" \
    --inpath \"{inpath}\" \
    --outpath \"{outpath}\" \
    --overwrite \
    --batch_size 32 \
    --gpu_ids 0")

    parsed_samples = {}
    for conll_file, _ in to_parse_samples.items():
        path_to_read_conll = os.path.join(outpath, conll_file + ".conllu")
        with open(path_to_read_conll, "r") as infile:
            parsed_samples[conll_file] = infile.read()
    shutil.rmtree(path_tmp)

    return {
        "status": "success", 
        "data": {
            "ready": True,
            "parsed_samples": parsed_samples, 
            "model_info": model_info
            },
        }
