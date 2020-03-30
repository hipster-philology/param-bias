from Code.BuildCorpus.Bible.build import BuildBible
from glob import glob
import os
from collections import defaultdict


def __wordextract__(content):
    """ Parse a .tab content and return lemmas

    :param content: String
    :return: List of Words
    """
    tokens = content.split("\n")
    for token in tokens:
        tok = token.split("\t")
        if len(tok) > 3:
            yield tok[2]


class BuildGreek(BuildBible):
    """ Creator of data from Greek Treebank

    :param folders: the folders where the .txt files are located
    :type folders: [str]
    :param dest: the directory in which to save the transformed corpus files
    :type dest: str
    """

    def __init__(self, folders, dest):
        self.filenames = []
        for folder in folders:
            self.filenames += glob('{}/**/*.tab'.format(folder), recursive=True)
        if not os.path.isdir(dest):
            os.makedirs(dest)
        self.dest = dest

    def build_word_list(self, f):
        """

        :param f: the function to use to extract the words
        :type f: function
        :return:
        :rtype:
        """

    def split_text(self):
        """ Separates the texts contained in the .tab files into a dictionary of lists where each sublist contains the
            line strings for each

        :return: dictionary of the split lists of word-containing strings. Split is based on split_level.
            The dictionary keys are the names of the split sections, e.g., corpus. book, chapter, verse
        :rtype: {str: list}
        """
        words = defaultdict(list)
        for file in self.filenames:
            with open(file) as f:
                words[os.path.basename(file)] = list(__wordextract__(f.read()))
        return words

    def build_transformed(self, cite_dict):
        """

        :param cite_dict: dictionary of all the citation units as keys and their list of words as values
        :type cite_dict: {str: list}
        """
        for c, words in cite_dict.items():
            dest_dir = '{}/{}'.format(self.dest, '/'.join(c.split('/')[:-1]))
            if not os.path.isdir(dest_dir):
                os.makedirs(dest_dir)
            with open('{}/{}.txt'.format(self.dest, c), mode='w') as f:
                f.write(' '.join(words))

    def run(self):
        """ Convenience function to run all functions in the class
        """
        self.build_transformed(self.split_text())
