import numpy as np
from sklearn.metrics.pairwise import pairwise_distances


def calc_dist_self(matrix, metrics='cosine'):
    return pairwise_distances(matrix, metric=metrics )

def calc_dist_pair(matrix1, matrix2, metrics='cosine'):
    return pairwise_distances(matrix1, matrix2, metric=metrics)


