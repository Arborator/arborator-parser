/home/arboratorgrew/miniconda3/envs/kirian/bin/python3 \
    /home/arboratorgrew/arborator-parser/BertForDeprel/BertForDeprel/run.py train \
    --ftrain /home/arboratorgrew/SUD_all_treebanks_utilities/data/all_together/ \
    --model_folder_path /home/arboratorgrew/arborator-parser_models_prod/_PRETRAINED/SUD_all_native_treebaks_GLOT_500_lr00005 \
    --batch_size 16  \
    --max_epoch 150  \
    --patience 10  \
    --split_ratio 0.98 \
    --embedding_type cis-lmu/glot500-base