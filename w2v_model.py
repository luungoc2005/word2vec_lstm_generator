import numpy as np
import string
from collections import defaultdict
from sklearn.base import BaseEstimator, TransformerMixin
from scipy.spatial import distance
# from sklearn.feature_extraction.text import TfidfVectorizer

WORD2VEC = None
WORD2VEC_FILE = 'glove/glove.6B.100d.txt'

def init_w2v():
    global WORD2VEC
    if not WORD2VEC:
        print('Importing %s...' % WORD2VEC_FILE)
        with open(WORD2VEC_FILE, 'r') as lines:
            WORD2VEC = {
                line.split()[0]: np.array(list(map(float, line.split()[1:])), dtype='float16')
                for line in lines
            }
    return WORD2VEC


class Word2VecVectorizer(BaseEstimator, TransformerMixin):

    def __init__(self, word2vec=None, sent_size=7):
        self.word2vec = word2vec or init_w2v()
        self.punct = list(set(string.punctuation))
        self.sent_size = sent_size
        # if a text is empty we should return a vector of zeros
        # with the same dimensionality as all the other vectors
        self.w2v_dim = len(iter(self.word2vec.values()).__next__())
        self.punct_length = len(self.punct)
        self.dim =  self.w2v_dim + self.punct_length

    def get_weight(self, punct):
        return np.append(np.zeros(self.w2v_dim, dtype='float16'),
            np.array([1.0 if punct == X else 0.0 for X in self.punct], dtype='float16'))

    def transform_single(self, w):
        return np.pad(self.word2vec[w], (0, self.punct_length), 'constant') \
            if w in self.word2vec.keys() \
            else self.get_weight(w)

    def inverse_transform_single(self, X):
        X_vec = X[:self.w2v_dim]
        if np.any(X_vec):
            min_dist = None
            min_word = ''
            for word in self.word2vec.keys():
                dist = np.linalg.norm(self.word2vec[word] - X_vec)
                # dist = distance.euclidean(self.word2vec[word], X_vec)
                if min_dist is None or dist < min_dist:
                    min_dist = dist
                    min_word = word
            return min_word
        else:
            indice = np.nonzero(X[self.w2v_dim:])
            if not indice:
                return ''
            else:
                return self.punct[indice[0]]

    def fit(self, X, y):
        return self

    def transform(self, X):
        if not X:
            return np.zeros((self.sent_size, self.dim), dtype='float16')
        return self.transform_sent(X)

    def transform_sent(self, X):
        pad_size = self.sent_size - len(X)
        if pad_size > 0:
            return np.pad([
                self.transform_single(w)
                for w in X
            ], ((0, pad_size), (0, 0)), 'constant')
        else:
            return np.array([
                self.transform_single(w)
                for w in X[:self.sent_size]
            ])