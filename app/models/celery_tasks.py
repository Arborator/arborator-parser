import json
import os
import shutil
import time
from typing import Dict, List
from celery import shared_task
from .service import ModelService, PATH_BERTFORDEPREL_VENV, PATH_BERTFORDEPREL_SCRIPT


@shared_task()
def train_model(model_info: Dict[str, str], train_samples: Dict[str, str], max_epoch: int):
    root_folder_path = ModelService.make_root_folder_path_from_model_info(model_info)
    os.makedirs(root_folder_path, exist_ok=True)

    train_files_folder_path = os.path.join(root_folder_path, "train_conlls")
    os.makedirs(train_files_folder_path, exist_ok=True)

    for sample_name, sample_content in train_samples.items():
        sample_path = os.path.join(train_files_folder_path, sample_name + ".conllu")
        with open(sample_path, "w") as outfile:
            outfile.write(sample_content)

    os.system(f"{PATH_BERTFORDEPREL_VENV} {PATH_BERTFORDEPREL_SCRIPT} train \
    --root_folder_path \"{root_folder_path}\" \
    --ftrain \"{train_files_folder_path}\" \
    --model_name \"kirparser\" \
    --batch_size 16 \
    --gpu_ids 0 \
    --conf_pretrain /models/SUD_all/SUD_all_1.config.json \
    --overwrite_pretrain_classifiers \
    --max_epoch {max_epoch}") 

    path_success_file = os.path.join(root_folder_path, "training_task_state.json")
    with open(path_success_file, "w") as outfile:
        outfile.write(json.dumps({"training_state": "DONE"}))

    return model_info



@shared_task()
def parse_sentences(model_info: Dict[str, str], to_parse_samples: Dict[str, str]) -> bool:
    root_folder_path = ModelService.make_root_folder_path_from_model_info(model_info)

    model_config_path = os.path.join(root_folder_path, "kirparser.config.json")

    time_now_str = str(int(time.time()))
    
    path_tmp = os.path.join(root_folder_path, time_now_str)

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

    return {"parsed_samples": parsed_samples, "model_info": model_info}

# def sha512_foldername(conll_names, conll_set_list, parser_id, dev_set, epochs, keep_upos):
#     input_string_ls = [str(parser_id), str(dev_set), str(epochs), str(keep_upos)]+conll_names
#     for conll in conll_set_list:
#         input_string_ls.append(re.sub(comment_pattern_tosub ,'', conll).strip()  )
#     input_string = '\n\n'.join(input_string_ls)
#     # base64.b64encode(hashlib.sha512(whateverString.encode()).digest())
#     return hashlib.sha256(input_string.encode()).hexdigest()