import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import pairwise_distances
import math

class ComputeDistance:

    def __init__(self, arr, ind, path):
        """

        :param arr: the array from which the co-occurrence statistical significance scores (e.g., LL) will be drawn
        :type arr: np.ndarray or np.memmap
        :param ind: the index of words for arr
        :type ind: list
        :param path: the path of the pickled dictionary of the semantic sub-domains and the words in those domains
        :type path: str
        """

        self.domains = pd.read_pickle(path)
        self.sig = pd.DataFrame(arr, index=ind, columns=ind)
        self.domain_averages = {}
        self.scores = {}

    def calc_centers(self):
        """ Calculates one vector representing the center of each sub-domain by taking the mean of the word cooccurrence significance vectors

        """

        for domain, words in self.domains.items():
            for word in words:
                try:
                    summed_score += self.sig.ix[word.lower(), :]
                except KeyError as E:
                    print(word.lower())
                except:
                    summed_score = self.sig.ix[word.lower(), :]
            self.domain_averages[domain] = summed_score/len(words)
            summed_score = None

    def score_calc(self):
        """ Calculates the mean similarity of each word with each domain
            similarities[0] will always be the similarity score of a word with its proper domain

        """
        similarities = []
        for domain, words in self.domains.items():
            for word in words:
                y = ((self.domain_averages[domain] * 10) - self.sig.ix[word.lower(), :]) / 9
                first = 1 - pairwise_distances(y.reshape(1, -1), self.sig.ix[word.lower(), :].reshape(1, -1),
                                               metric='cosine')[0][0]
                s = [first]
                for domain2 in self.domains.keys():
                    if domain2 != domain:
                        other = self.domain_averages[domain2]
                        s.append(1 -
                                 pairwise_distances(other.reshape(1, -1), self.sig.ix[word.lower(), :].reshape(1, -1),
                                                    metric='cosine')[0][0])
                similarities.append({word: s})
        self.record_scores(similarities)

    def record_scores(self, sims):
        """ records which words are closest to their proper domain as opposed to any other domain

        :param sims: the similarity scores of a word with all semantic domains
        :type sims: list
        """
        for x in sims:
            for word, v in x.items():
                if max(v) == v[0]:
                    self.scores[word] = 1


class CrossDomainAccuracy(ComputeDistance):

    def record_scores(self, sims):
        """ records math.e ** (the rank of each word's similarity score) with its domain when compared to its scores to the other domains
            E.g., if its rank with its own domain is 2, this records the value math.e ** 2 for that word.
            To finish the calculation of the Cross-Domain Accuracy, the values here need to be put into the equation
            1 / score ** ρ, where ρ is the constant chosen to weight misattribution.

        :param sims: the similarity scores of a word with all semantic domains
        :type sims: list
        """
        for x in sims:
            for word, v in x.items():
                ranked = sorted(v, reverse=True)
                self.scores[word] = math.e ** ranked.index(v[0])


class SameDomainAccuracy(ComputeDistance):

    def __init__(self, arr, ind, path, delta=1.0):
        """

        :param arr: the array from which the co-occurrence statistical significance scores (e.g., LL) will be drawn
        :type arr: np.ndarray or np.memmap
        :param ind: the index of words for arr
        :type ind: list
        :param path: the path of the pickled dictionary of the semantic sub-domains and the words in those domains
        :type path: str
        """

        self.domains = pd.read_pickle(path)
        self.sig = pd.DataFrame(arr, index=ind, columns=ind)
        self.domain_averages = {}
        self.scores = {}
        self.Delta = delta

    def score_calc(self):
        """ Calculates the Same-Domain Accuracy using the formula 1 - (Σ(i=1, m(k(l))) ((Δ - sim(w(i), w(n)))**2)/m(k(l)))
            Note: the sklearn.metrics.pairwise.pairwise_distances function using metric="cosine" == 1 - CosSim

        """

        for domain, words in self.domains.items():
            for word in words:
                summed_score = 0
                for word2 in words:
                    if word2 != word:
                        try:
                            summed_score += (self.Delta - (1 - pairwise_distances(
                                self.sig.ix[word2.lower(), :].reshape(1, -1),
                                self.sig.ix[word.lower(), :].reshape(1, -1),
                                metric='cosine'
                            )[0][0]))**2
                        except KeyError as E:
                            print(word.lower(), word2.lower())
                        except:
                            summed_score = (self.Delta - (1 - pairwise_distances(
                                self.sig.ix[word2.lower(), :].reshape(1, -1),
                                self.sig.ix[word.lower(), :].reshape(1, -1),
                                metric='cosine'
                            )[0][0]))**2
                self.scores[word] = 1 - (summed_score / len(words)-1)

def SemDomainAttribAccuracy(CDD, SDD, alpha=1, rho=1):
    """ computes the Semantic Domain Attribution Accuracy Score
        alpha: 0 <= alpha <= 2, a value of 1 balances between CDD and SDD, >1 SDD is more important, <1 CDD is more important
        rho: 0 < rho < 1 will not weight misattribution in CDD very heavily, 1 < rho < inf will weight misattribution more heavily

    :param CDD: the raw CDD scores for each word equal to math.e ** rank(w(n), k(l))
    :type CDD: {word: score}
    :param SDD: the SDD scores for each word
    :type SDD: {word: score}
    :param alpha: the value for weighting the importance of SDD and CDD, the higher the value, the more important SDD is
    :type alpha: float
    :param rho: the value for weighting misattributions in CDD, the higher the value, the more weight misattribution has
    :type rho: float
    :return: the SDA score for each word
    :rtype: {word: score}
    """
    assert alpha >= 0, "The value of alpha must be between 0 and 2"
    assert alpha <= 2, "The value of alpha must be between 0 and 2"
    assert rho > 0, "The value of rho must be greater than 0"

    scores = {}
    for word in CDD.keys():
        try:
            scores[word] = ((alpha * SDD[word]) + ((2 - alpha) * (1 / (CDD[word] ** rho)))) / 2
        except OverflowError as E:
            print(E, word, SDD[word], CDD[word])

    return scores