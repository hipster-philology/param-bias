import os
import re
from collections import defaultdict
from glob import glob

from Code.BuildCorpus.Bible.utils import word_extract, word_cite_extract


class BuildBible(object):
    SPLITLEVELDICT = {
        'none': 0,
        'corpus': 0,
        'book': 3,
        'chapter': 2,
        'verse': 1
    }

    def __init__(self, folders, dest, split_level, re_pattern='.+?lem="([^"]*).*'):
        """

        :param folders: the folders where the .txt files are located
        :type folders: [str]
        :param dest: the directory in which to save the transformed corpus files
        :type dest: str
        :param split_level: the level at which to split
            'none': all files in all folders are joined together in one large .txt file
            'corpus': all files in each of the folders are joined with each other, producing as many .txt files as folders
            'book': one .txt file is produced for each biblical book
            'chapter': one .txt file is produced for each chapter in each book
            'verse': one .txt file is produced for each verse in each chapter of each book
        :type split_level: str
        :param re_pattern: the regex pattern that will find the desired words
        :type re_pattern: str
        """
        self.filenames = []
        for folder in folders:
            self.filenames += glob('{}/*.txt'.format(folder))
        if not os.path.isdir(dest):
            os.makedirs(dest)
        self.dest = dest
        self.split_level = split_level
        self.pattern = r'{}'.format(re_pattern)

    def build_word_list(self, f):
        """

        :param f: the function to use to extract the words
        :type f: function
        :return:
        :rtype:
        """

    def split_text(self):
        """ Separates the texts contained in the .txt files into a dictionary of lists where each sublist contains the
            line strings for each

        :return: dictionary of the split lists of word-containing strings. Split is based on split_level.
            The dictionary keys are the names of the split sections, e.g., corpus. book, chapter, verse
        :rtype: {str: list}
        """
        words = defaultdict(list)
        if self.split_level == 'none':
            for file in self.filenames:
                with open(file) as f:
                    words['Full'] += word_extract(f.read().split('\n'), self.pattern)
            return words
        elif self.split_level == 'corpus':
            for file in self.filenames:
                corpus = file.split('/')[-2]
                with open(file) as f:
                    words[corpus] += word_extract(f.read().split('\n'), self.pattern)
            return words
        else:
            join_int = self.SPLITLEVELDICT[self.split_level]
            for file in self.filenames:
                corpus = file.split('/')[-2]
                with open(file) as f:
                    words.update(word_cite_extract(f.read().split('\n'), self.pattern, join_int, corpus))
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
            if self.SPLITLEVELDICT[self.split_level] != 0:
                dest_dir = re.sub(r"NT|LXX", 'Full', dest_dir)
                if not os.path.isdir(dest_dir):
                    os.makedirs(dest_dir)
                c = re.sub(r'NT|LXX', 'Full', c)
                with open('{}/{}.txt'.format(self.dest, c), mode='w') as f:
                    f.write(' '.join(words))

    def run(self):
        """ Convenience function to run all functions in the class
        """
        self.build_transformed(self.split_text())
