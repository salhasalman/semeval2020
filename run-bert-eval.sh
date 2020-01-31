# For compatibility with server
project_path=$1

# Unzip trial data
unzip -o $project_path/eval_data.zip

# Make folders
mkdir -p $project_path/eval_matrices/
mkdir -p $project_path/eval_results/

# Iterate over languages (ONLY DATASET IS COHA FOR NOW)
declare -a languages=(english)
for language in "${languages[@]}"
do

    # Make folders
    mkdir -p $project_path/eval_matrices/$language/
    mkdir -p $project_path/eval_results/$language/

    # Collect contextualised representations
    python3 $project_path/code/bert/collect.py $project_path/models/bert/$language/config.txt $project_path/eval_data/corpora/$language/corpus1 $project_path/eval_data/targets/$language.txt $project_path/eval_matrices/$language/bert_corpus1.dict
    python3 $project_path/code/bert/collect.py $project_path/models/bert/$language/config.txt $project_path/eval_data/corpora/$language/corpus2 $project_path/eval_data/targets/$language.txt $project_path/eval_matrices/$language/bert_corpus2.dict

    # Compute diachronic average pairwise distance
    python3 $project_path/code/bert/distance.py $project_path/eval_data/targets/$language.txt $project_path/eval_matrices/$language/bert_corpus1.dict $project_path/eval_matrices/$language/bert_corpus2.dict $project_path/eval_results/$language/bert_avg_pw_dist.csv

    # Compute diachronic (absolute) difference in mean relatedness
    python3 $project_path/code/bert/relatedness.py -a $project_path/eval_data/targets/$language.txt $project_path/eval_matrices/$language/bert_corpus1.dict $project_path/eval_matrices/$language/bert_corpus2.dict $project_path/eval_results/$language/bert_mean_rel_diff.csv

    # Classify results into two classes according to threshold
    python3 $project_path/code/class.py $project_path/eval_results/$language/bert_avg_pw_dist.csv $project_path/eval_results/$language/bert_avg_pw_dist_classes.csv 0.5
    python3 $project_path/code/class.py $project_path/eval_results/$language/bert_mean_rel_diff.csv $project_path/eval_results/$language/bert_mean_rel_diff_classes.csv 0.04


    ### Make answer files for submission ###

    # average pairwise distance
    mkdir -p $project_path/eval_results/answer/task2/ && cp $project_path/eval_results/$language/bert_avg_pw_dist.csv $project_path/eval_results/answer/task2/$language.txt
    mkdir -p $project_path/eval_results/answer/task1/ && cp $project_path/eval_results/$language/bert_avg_pw_dist_classes.csv $project_path/eval_results/answer/task1/$language.txt
    cd $project_path/eval_results/ && zip -r answer_bert_avg_pw_dist.zip $project_path/answer/ && rm -r $project_path/answer/ && cd $project_path/

    # difference in mean relatedness
    mkdir -p $project_path/eval_results/answer/task2/ && cp $project_path/eval_results/$language/bert_mean_rel_diff.csv $project_path/eval_results/answer/task2/$language.txt
    mkdir -p $project_path/eval_results/answer/task1/ && cp $project_path/eval_results/$language/bert_mean_rel_diff_classes.csv $project_path/eval_results/answer/task1/$language.txt
    cd $project_path/eval_results/ && zip -r answer_bert_mean_rel_diff.zip $project_path/answer/ && rm -r $project_path/answer/ && cd $project_path/

done