# python3
# coding: utf-8

import numpy as np
from docopt import docopt
from tqdm import tqdm
from sklearn.cluster import DBSCAN, AffinityPropagation
from sklearn.preprocessing import StandardScaler
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def cluster(usage_matrix, algorithm, args_dict, word):
    """
    :param word: target word
    :param usage_matrix: a matrix of contextualised word representations of shape
    (num_usages, model_dim)
    :param algorithm:the clustering algorithm: DBSCAN or Affinity Propagation
    :param args_dict: the sklearn parameters of the chosen clustering algorithm
    :return: n_clusters - the number of clusters in the given usage matrix
             labels - a list of labels, one for each contextualised representation
    """
    if algorithm.lower() not in ['dbscan', 'db', 'affinity', 'affinity propagation', 'ap']:
        raise ValueError('Invalid clustering method:', algorithm)

    # logger.info('{} matrix shape: {}'.format(word, usage_matrix.shape))
    usage_matrix = StandardScaler().fit_transform(usage_matrix)

    if algorithm.lower() in ['dbscan', 'db']:
        clustering = DBSCAN(**args_dict).fit(usage_matrix)
        labels = clustering.labels_
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    else:
        clustering = AffinityPropagation(**args_dict).fit(usage_matrix)
        labels = clustering.labels_
        n_clusters = len(set(labels))

    assert len(labels) == usage_matrix.shape[0]
    logger.info('{} has {} clusters'.format(word, n_clusters))
    return n_clusters, labels


def get_num_senses(filepath, algorithm, args_dict, words):
    """
    :param filepath: path to .npz file containing a dictionary
    {lemma: usage matrix for lemma in targets}
    :param algorithm: the clustering algorithm: DBSCAN or Affinity Propagation
    :param args_dict: the sklearn parameters of the chosen clustering algorithm
    :param words: set of target words
    :return: num_senses - a dictionary {lemma: num_senses_lemma for lemma in targets}
    """
    usage_dict = np.load(filepath)
    num_senses = {w: 0 for w in words}

    for word in tqdm(num_senses):
        if word in usage_dict:
            if usage_dict[word].shape[0] > 0:
                num_senses_w, _ = cluster(usage_dict[word], algorithm, args_dict, word)
                num_senses[word] = num_senses_w
    return num_senses


def main():
    """
    Get number of senses given two diachronic sets of usage representations.
    """

    # Get the arguments
    args = docopt("""Get number of senses for two sets of usage representations.

    Usage:
        cluster.py <targets> <representationsFile1> <representationsFile2> <outPath1> <outPath2>

    Arguments:
        <targets> = path to target words file
        <representationsFile1> = path to .npz file containing a dictionary that maps words to usage matrices (corpus1)
        <representationsFile2> = path to .npz file containing a dictionary that maps words to usage matrices (corpus2)
        <outPath1> = output filepath *without extension* for csv file with number of senses for corpus 1
                    (format: 'lemma sense_id label related_terms')
        <outPath2> = output filepath *without extension* for csv file with number of senses for corpus 2
                    (format: 'lemma sense_id label related_terms')
    """)

    CLUSTERING = 'AP'

    target_words = set([w.strip() for w in open(args['<targets>'], 'r').readlines()])

    filepath1 = args['<representationsFile1>']
    filepath2 = args['<representationsFile2>']
    outPath1 = args['<outPath1>']
    outPath2 = args['<outPath2>']

    args_dicts = {
        'DB': {
            'eps': 0.5,
            'min_samples': 5,
            'metric': 'euclidean',
            'algorithm': 'auto',
            'leaf_size': 30,
            'p': None,
        },
        'AP': {
            'damping': 0.5,
            'max_iter': 150,
            'convergence_iter': 15,
            'preference': None,
            'affinity': 'euclidean'
        }
    }

    logger.info('Clustering using %s' % CLUSTERING)

    for filepath, outfile in zip([filepath1, filepath2], [outPath1, outPath2]):
        senses = get_num_senses(filepath, CLUSTERING, args_dicts[CLUSTERING], target_words)
        with open('{}.csv'.format(outfile), 'w') as f:
            f.write('word\tcid\tkeyword\tcluster\n')
            for w in senses:
                for sense in range(senses[w]):
                    f.write("{}\t{}\t{}\t{}\n".format(w, sense, 'label', 'related_terms'))


if __name__ == '__main__':
    main()
