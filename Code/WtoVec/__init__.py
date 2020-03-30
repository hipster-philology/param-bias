from gensim.models.word2vec import Word2Vec, LineSentence
from glob import glob
from os.path import join, isdir
from os import mkdir
from collections import Counter


class W2VModel(object):
    """ Word2Vec trained model

    :param name: Name of the Model that we train
    :param directory: Input data directory
    :param parameters: Dictionary of parameters for .train()
    :param output_dir: Output data directory
    :param preload: Preload a pre-trained model
    :param epochs: Number of epochs
    :param additional_words: Set of words from other models
    """
    def __init__(self, name, directory, epochs=500, parameters=None, output_dir="models", preload=None, additional_words=None):
        self.name = name
        self.directory = directory
        self.parameters = parameters
        self.epochs = epochs
        self.parameters = dict()
        if parameters is not None:
            self.parameters.update(parameters)
        if not isdir(output_dir):
            mkdir(output_dir)
        self.output_dir = output_dir
        self.preload = preload
        self.__model__ = None
        self.__files__ = None
        self.__sentences__ = None
        self.additional_words = additional_words
        self.__words__ = None
        self.__occurences__ = None

    @property
    def model(self):
        """ Model

        :return: Model
        :rtype: Word2Vec
        """
        return self.__model__

    @property
    def texts(self):
        """ Generator yield the list of files that are supposed to form the corpus
        """
        if isinstance(self.directory, list):
            for directory in self.directory:
                for file in glob(join(directory, "**/*.txt"), recursive=True):
                    yield file
        elif self.directory.endswith(".txt"):
            yield self.directory
        else:
            for x in glob(join(self.directory, "**/*.txt"), recursive=True):
                yield x

    @property
    def files(self):
        """ List of files content
        """
        if self.__files__ is None:
            self.__files__ = []
            for text in self.texts:
                with open(text) as f:
                    self.__files__.append(f.read())
        return self.__files__

    @property
    def sentences(self):
        """ List of sentences
        """
        if self.__sentences__ is None:
            self.__sentences__ = [s.split() for s in self.files]
        return self.__sentences__

    @property
    def words(self):
        """ Vocabulary (Set of words)
        """
        if self.__words__ is None:
            self.__words__ = [w for s in self.files for w in s.split()]
            if self.additional_words:
                self.__words__ += self.additional_words
            self.__words__ = list(set(self.__words__))
        return self.__words__

    @property
    def count(self):
        """ Number of unique words """
        return len(self.words)

    @property
    def output(self):
        """ Name of the output model """
        return join(self.output_dir, self.name+".model")

    def train(self):
        """ Training method """
        if self.__model__ is None:
            if self.preload is not None:
                self.__model__ = Word2Vec.load(self.preload.output)
            else:
                self.__model__ = Word2Vec(**self.parameters)
                self.model.build_vocab(self.sentences)
        self.model.train(self.sentences, total_examples=self.count, epochs=self.epochs)
        self.model.save(self.output)

    def load(self):
        """ Load the model """
        self.__model__ = Word2Vec.load(self.output)

    def similarity(self, w1, w2):
        """ Compute the similarity between two words """
        return self.model.similarity(w1, w2)

    def doesnt_match(self, words):
        """ In a list of words, tell which one is not fitting in the group"""
        return self.model.doesnt_match(words)

    def most_similar(self, word, n=5):
        """ Compute the @n similar words to @word """
        return self.model.most_similar([word], topn=n)  # + self.model.most_similar(negative=[word], topn=n)

    @property
    def occurences(self):
        """ Dictionary of occurrences """
        if self.__occurences__ is None:
            self.__occurences__ = Counter([w for s in self.files for w in s.split()])
        return self.__occurences__
