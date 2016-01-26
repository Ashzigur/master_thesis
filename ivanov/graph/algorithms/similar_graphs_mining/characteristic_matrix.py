'''
Created on Jan 13, 2016

@author: Ivan Ivanov
'''
from ivanov.graph.algorithms.similar_graphs_mining import feature_extraction,\
    shingle_extraction, fingerprint
from ivanov.inout.serializable import Serializable
import numpy as np
import itertools

class CharacteristicMatrix(Serializable):
    
#     @staticmethod
#     def estimate_time_to_build(nodes_count, features_per_node = 100):
#         '''Get the estimated time to build the characteristic matrix in seconds.
#         '''
#         time_per_feature = 0.001
#         return nodes_count * features_per_node * time_per_feature
    
    def build(self, feature_lists):
        self.sparse_matrix = {}
        i = -1
        for element_features in feature_lists:
            i += 1
            for feature in element_features:
                shingles = shingle_extraction.extract_shingles(feature)
                fingerprints = fingerprint.get_fingerprints(shingles)
                for fp in fingerprints:
                    if not self.sparse_matrix.has_key(fp):
                        self.sparse_matrix[fp] = set()
                    self.sparse_matrix[fp].add(i)
    
    def compute_jaccard_similarity_matrix(self):
        cols_cache = {}
        def get_shingles_fp_set(col):
            if col in cols_cache:
                return cols_cache[col]
            else:
                shingles_fp = set()
                for row in self.sparse_matrix:
                    if col in self.sparse_matrix[row]:
                        shingles_fp.add(row)
                cols_cache[col] = shingles_fp
                return shingles_fp
        
        def jaccard_sim(u, v):
            return float(len(u.intersection(v))) / float(len(u.union(v)))
        
        jaccard_sim_mat = np.zeros((self.cols_count, self.cols_count), dtype=np.float32)
        
        for col_1, col_2 in itertools.combinations(range(self.cols_count), 2):
            shingles_col_1 = get_shingles_fp_set(col_1)
            shingles_col_2 = get_shingles_fp_set(col_2)
            jaccard_sim_mat[col_1, col_2] = jaccard_sim(shingles_col_1, shingles_col_2)
        
        return jaccard_sim_mat
    
    def non_empty_rows(self):
        return self.sparse_matrix.keys()
    
    def non_empty_rows_count(self):
        return len(self.sparse_matrix.keys())
    
    def __getitem__(self, key):
        return self.sparse_matrix[key]
    
    def __eq__(self, other):
        if isinstance(other, CharacteristicMatrix):
            return self.sparse_matrix == other.sparse_matrix
        else:
            return False
    
    def __ne__(self, other):
        return not self.__eq__(other)

    def __init__(self, graph_database, wl_iterations=0):
        '''
        :param graph_database: A list of lists where each sublist represents
        an element of the database (will be represented by a column in the
        characteristic matrix), and each element in a sublist is a hypegraph.
        (One element can be represented by multiple graphs)
        :param wl_iterations: Number of Weisfeiler-Lahman iterations to be
        performed (before a graph becomes 'stable').
        '''
        self.cols_count = len(graph_database)
        
        feature_lists = feature_extraction.get_feature_lists(graph_database, wl_iterations)
        self.build(feature_lists)