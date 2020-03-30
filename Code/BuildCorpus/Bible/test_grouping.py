import random
from glob import glob

class CreateTestGroups(object):

    def __init__(self, source, dest, count_1=3, count_2=1, min_size=1):
        """

        :param source: the source folder where the domain .txt files are located
        :type source: str
        :param dest: the .txt file in which to save the testing TSV file
        :type dest: str
        :param count_1: the number of words to select for each testing group from the primary domain
        :type count_1: int
        :param count_2: the number of words to select for each testing group from the secondary domain
        :type count_2: int
        :param min_size: the number of words that each domain should contain
        :type min_size: int
        """
        self.domains = {}
        for file in glob('{}/*.txt'.format(source)):
            with open(file) as f:
                self.domains[file.split('/')[-1]] = f.read().strip().split()
        self.dest = dest
        self.count_1 = count_1
        self.count_2 = count_2
        self.min_size = min_size

    @staticmethod
    def load_TSV(source):
        """ Loads an existing TSV file with testing groups

        :return: list of testing groups
        :rtype: [([str], [str])]
        """
        testing = []
        with open(source) as f:
            groups = f.read().strip().split('\n')
        for group in groups:
            elements = group.split('\t')
            good = elements[4:-int(elements[3])]
            bad = elements[-int(elements[3]):]
            testing.append((good, bad))
        return testing

    def produce_domain_pairs(self):
        """ Produces random pairs based on the following guidelines:
                the pair isn't made up of the same two sub-domains
                the two subdomains do not belong to the same parent domain
                both subdomains have at least 10 elements
                the two subdomains share no words in common
            These results should be checked by hand to ensure that the domains do not overlap with each other too much.

        :return: pairs of domains
        :rtype: list
        """
        pairs = []
        names = list(self.domains.keys())
        while len(pairs) < 100:
            x = random.randrange(len(self.domains))
            y = random.randrange(len(self.domains))

            if names[x][:3] == names[y][:3] or names[x][:3] == '(93':
                continue

            x_words = self.domains[names[x]]
            y_words = self.domains[names[y]]

            if len(x_words) < self.min_size or len(y_words) < self.min_size:
                continue

            for w in x_words:
                if w in y_words:
                    break
            if '{}\t{}'.format(names[x], names[y]) not in pairs:
                pairs.append('{}\t{}'.format(names[x], names[y]))
        return pairs

    def produce_testing_TSV(self, pairs):
        """ Produces a TSV file where each line represents a group of words to be tested.
            Each line will have the following format (each | represents a tab):
                | Domain 1 | Domain 2 | Nb Original | Nb Second | Word 1 | Word 2 | Word 3 | etc.

        :param pairs:
        :type pairs:
        :return: test_groups
        :rtype: list
        """
        test_groups = []
        for pair in pairs:
            domain1, domain2 = pair.split('\t')
            words_1 = self.build_word_list(domain1, self.count_1)
            words_2 = self.build_word_list(domain2, self.count_2)
            group = '{d1}\t{d2}\t{n1}\t{n2}\t{w1}\t{w2}'.format(d1=domain1,
                                                                d2=domain2,
                                                                n1=self.count_1,
                                                                n2=self.count_2,
                                                                w1='\t'.join(words_1),
                                                                w2='\t'.join(words_2))
            test_groups.append(group)
        return test_groups

    def build_word_list(self, domain, length):
        """ Builds a random list of words from self.domains[domain] where the length of the list == length

        :param domain: the name of the domain from which to draw words
        :type domain: str
        :param length: the length of the list of words to be produced
        :type length: int
        :return: list of words
        :rtype: list
        """
        words = []
        while len(words) < length:
            w = self.domains[domain][random.randrange(len(self.domains[domain]))]
            if w not in words:
                words.append(w)
        return words

    def run(self):
        """ Convenience function to run all steps in the process

        """
        with open(self.dest, mode="w") as f:
            f.write('\n'.join(self.produce_testing_TSV(self.produce_domain_pairs())))
