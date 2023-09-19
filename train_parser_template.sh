# # this script is a quick proto script for testing the training of change_while_grokking new branch of BertForDeprel
PYTHON_PATH=/home/arboratorgrew/arborator-parser/BertForDeprel/.venv/bin/python
TRAINER_PATH=/home/arboratorgrew/arborator-parser/BertForDeprel/BertForDeprel/run.py 

MODELS_PATH=/home/arboratorgrew/arborator-parser_models_prod/

DATA_ALL_FOLDER_PATH=/home/arboratorgrew/SUD_all_treebanks_utilities/data/all_together/
DATA_PER_LANGUAGES_FOLDERS_PATH=/home/arboratorgrew/SUD_all_treebanks_utilities/data/gold/


$PYTHON_PATH $TRAINER_PATH \
    train \
    --ftrain $DATA_ALL_FOLDER_PATH \
    --new_model_path $MODELS_PATH/PRETRAINED/SUD_ALL/ \
    --batch_size 16  \
    --max_epoch 50  \
    --patience 10  \
    --gpu_ids 0 

# # PARSING : to debug small stuff
# /home/arboratorgrew/arborator-parser/BertForDeprel/.venv/bin/python /home/arboratorgrew/arborator-parser/BertForDeprel/BertForDeprel/run.py \
#         predict \
#         --model_path /home/arboratorgrew/arborator-parser_models_dev/chinese_grammar_wiki_morphSUD/2023-09-05_12\:16\:07.344/ \
#         --overwrite \
#         --inpath /home/arboratorgrew/arborator-parser_models_dev/chinese_grammar_wiki_morphSUD/2023-09-05_12:16:07.344/1693914266/to_predict \
#         --outpath /home/arboratorgrew/arborator-parser_models_dev/chinese_grammar_wiki_morphSUD/2023-09-05_12:16:07.344/1693914266/predicted \
#         --batch_size 32 