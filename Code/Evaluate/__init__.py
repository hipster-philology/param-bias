from Code.BuildCorpus.Bible.test_grouping import CreateTestGroups
from Code.WtoVec import W2VModel
import math
from statistics import mean
from os.path import basename, dirname
from pandas import DataFrame, read_pickle
from Code.utils import pandas_most_sim
from collections import namedtuple


class Evaluator(object):
    """ Evaluate a word2vec model

    :param w2vec: Code.WtoVec.W2VModel
    :param test_data_path: Path to the tsv file
    :type test_data_path: str
    """
    def __init__(self, w2vec, test_data_path):
        self.w2vec = w2vec
        if type(self.w2vec) is DataFrame:
            self.w2vec.most_similar = self.pandas_most_sim
            self.w2vec.similarity = self.pandas_similarity
            self.occ_dict = read_pickle('data/original/SBLGNT_lem_dict.pickle')
        self.test_data = CreateTestGroups.load_TSV(test_data_path)
        self.top_score = {}

    def single_score(self, fitting, alien):
        """ Compute the score for fitting and alien words in a row

        :param fitting: Fitting words
        :param alien: Alien Words
        :return: List of scores
        """
        good, outlier = [], []
        for fitting_single in fitting:
            others = [w for w in fitting if w != fitting_single]
            good.append(self.gap_score(fitting_single, others))
        for alien_single in alien:
            outlier.append(self.gap_score(alien_single, fitting))
        return good, outlier

    def gap_score(self, source, targets):
        """ Compute the GAP score for a word

        :param source: A single word for which we compute Gap score
        :param targets: List of target with which we compute Gap
        :return:
        """
        if source not in self.top_score:
            self.top_score[source] = mean([score for _, score in self.w2vec.most_similar(source)])
        score = [
            math.pow(self.top_score[source] - max([self.w2vec.similarity(source, target), 0]), 1)
            for target in targets
        ]
        return sum(score) / len(score)

    def score(self, filename="score.tsv", nomatch=False):
        """ Compute scores for the text

        :param filename: Name of the output file
        :param nomatch: Compute Gensim.NoMatch
        :return:
        """
        lines = [
        ]
        scores = []
        row = 0

        for (good_words, bad_words) in self.test_data:
            try:
                good, outlier = self.single_score(good_words, bad_words)
                scores.append([good, outlier])
                mgood, moutlier = mean(good), mean(outlier)
                if type(self.w2vec) is W2VModel:
                    occs = [str(self.w2vec.occurences[w]) for w in good_words+bad_words]
                    doesnotmatch = self.w2vec.doesnt_match(good_words + bad_words)
                    doesnotmatch_score = 0
                    if doesnotmatch in bad_words:
                        doesnotmatch_score = 1
                else:
                    occs = [str(self.occ_dict[w]) for w in good_words+bad_words]
                    doesnotmatch = 'None'
                    doesnotmatch_score = 0

                lines.append(
                    "\t".join(
                        [str(moutlier - mgood)] + good_words + bad_words +
                        [doesnotmatch, str(doesnotmatch_score)] +
                        occs +
                        [" ; ".join([str(s) for s in self.w2vec.most_similar(w, n=1)[0]]) for w in good_words+bad_words]
                    )
                )

            except Exception as E:
                pass
                print("Row {} is failing ({})".format(row, E))
            row += 1

        with open(filename, "w") as f:
            f.write(
                "\t".join(
                    ["Mean Gap Score Difference"] +
                    ["IntraDomainWord"]*len(good_words) +
                    ["ExtraDomainWord"]*len(bad_words) +
                    ["Gensim Computed Outsider", "Right Computer Outsider"] +
                    ["Occurences W{}".format(str(i)) for i in range(0, len(occs))] +
                    ["Most similar word to W{}".format(str(i)) for i in range(0, len(occs))]
                ) + "\n"
            )
            f.write("\n".join(lines))

    def pandas_most_sim(self, target, n=5):
        """ finds the most similar candidate words to a target word

        :param target: the target word
        :type target: str
        :param n_candidates: the number of similaritiy candidates to return
        :type n_candidates: int
        :return: the n_candidate most similar words
        :rtype: list
        """
        target = target.lower()
        v = list(self.w2vec.ix[target].sort_values(ascending=False).head(n + 1))[1:]
        k = list(self.w2vec.ix[target].sort_values(ascending=False).head(n + 1).index)[1:]
        return [x for x in zip(k, v)]

    def pandas_similarity(self, w1, w2):
        """ finds the most similar candidate words to a target word

        :param w1: word 1
        :type target: str
        :param w2: word 2
        :type w2: str
        :return: the similarity score of the two words
        :rtype: list
        """
        return self.w2vec.ix[w1.lower()][w2.lower()]


class Gephi:
    """ Generates a network of word in the context of the W2Vec graph

    :param model: Path to the model file
    :param domain: Path to the domain text file
    :param topn: Number of top nodes needed to be taken
    """

    def __init__(self, model, domain, topn=5):
        self.model = W2VModel(basename(model).replace(".model", ""), dirname(model))
        self.model.load()

        with open(domain) as f:
            self.input = f.read().split("\n")

        # Sanitize data by removing unknown words
        sanitized = []
        for word in set(self.input):
            try:
                _ = self.model.most_similar(word, 1)
                sanitized.append(word)
            except (IndexError, KeyError):
                print("{} is not in the vocabulary".format(word))
        self.input = [] + sanitized

        self.additional_nodes = []
        self.nodes = []
        self.edges = []
        self.topn = topn

    def write(self, path):
        """ Write the nodes and edges in Path

        :param path: Path in which the user want to write the nodes. ex. : /path/to/results will make /path/to/results.\
        nodes.tsv and /path/to/results.edges.tsv
        """

        self.find_nodes()
        self.nodes = self.input + self.additional_nodes
        self.build_edges()
        with open(path+".nodes.tsv", "w") as f:
            f.write("\n".join(
                ["id\tlabel\ttype"] + [
                    "{}\t{}\t{}".format(
                        str(self.nodes.index(node)), node, str(int(node in self.input))
                    ) for node in self.nodes
                ]
            ))

        with open(path+".edges.tsv", "w") as f:
            f.write("\n".join(
                ["source\ttarget\tweight"] + [
                    "\t".join(edge) for edge in self.edges
                ]
            ))

    def find_nodes(self):
        """ Build nodes in the document
        """
        for word in self.input:
            self.additional_nodes += [
                new_word
                for new_word, *_ in self.model.most_similar(word, n=self.topn)
                if new_word not in self.additional_nodes + self.input
            ]
        self.additional_nodes = list(set(self.additional_nodes))

    def build_edges(self):
        """ Build the list of edges
        """
        for source in self.nodes:
            for target in [x for x in self.nodes if x != source]:
                source_index, target_index = self.nodes.index(source), self.nodes.index(target)
                self.edges.append([str(source_index), str(target_index), str(self.model.similarity(source, target))])
        return self.edges

if __name__ == "__main__":
    from Code.WtoVec import W2VModel
    for trained in ["no-", ""]:
        w2vec1 = W2VModel("com-cut."+trained+"pretrained.1500e.20w", "data/transformed/com-cut/Full")
        w2vec1.load()
        w2vec2 = W2VModel("com-cut."+trained+"pretrained.1500e.10w", "data/transformed/com-cut/Full")
        w2vec2.load()
        w2vec3 = W2VModel("com-cut."+trained+"pretrained.1500e", "data/transformed/com-cut/Full")
        w2vec3.load()

        eval1 = Evaluator(w2vec1, "data/testing_groups.txt")
        eval1.score("results/com-cut."+trained+"pretrained.1500e.20w.tsv")
        eval2 = Evaluator(w2vec2, "data/testing_groups.txt")
        eval2.score("results/com-cut."+trained+"pretrained.1500e.10w.tsv")
        eval3 = Evaluator(w2vec3, "data/testing_groups.txt")
        eval3.score("results/com-cut."+trained+"pretrained.1500e.tsv")