from nltk.corpus import wordnet as wn
from nltk import wordpunct_tokenize
from nltk import WordNetLemmatizer
from nltk import sent_tokenize
from nltk import pos_tag

from sklearn.base import BaseEstimator, TransformerMixin


class NLTKPreprocessor(BaseEstimator, TransformerMixin):

    def __init__(self, stopwords=[], punct=[],
                 lower=True, strip=True, lemmatize=True, ignore_type=[]):
        self.lower = lower
        self.strip = strip
        self.ignore_type = ignore_type
        self.stopwords = stopwords
        self.punct = punct
        self.do_lemmatize = lemmatize
        self.lemmatizer = WordNetLemmatizer()

    def fit(self, X, y=None):
        return self

    def inverse_transform(self, X):
        return [" ".join(doc) for doc in X]

    def transform(self, X):
        return [
            list(self.tokenize(doc)) for doc in X
        ]

    def tokenize(self, document):
        for sent in sent_tokenize(document):
            for token, tag in pos_tag(wordpunct_tokenize(sent)):
                token = token.lower() if self.lower else token
                token = token.strip() if self.strip else token
                token = token.strip('_') if self.strip else token
                token = token.strip('*') if self.strip else token

                if token in self.stopwords:
                    continue

                if all(char in self.punct for char in token):
                    continue
                
                if self.do_lemmatize:
                    lemma = self.lemmatize(token, tag, self.ignore_type)
                    yield lemma
                else:
                    yield token

    def lemmatize(self, token, tag, ignore_type=['N']):
        tag = {
            'N': wn.NOUN,
            'V': wn.VERB,
            'R': wn.ADV,
            'J': wn.ADJ
        }.get(tag[0], wn.NOUN)

        # Ignore nouns by default to account for plurals
        if tag in ignore_type:
            return token
        else:
            return self.lemmatizer.lemmatize(token, tag)
