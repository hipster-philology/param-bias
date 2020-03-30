import pickle

class BySize:

    def load_pickle(self, path):
        """ Loads the Louw-Nida category information from a pickled dictionary

        :param path: the path to the pickled Louw-Nida category information file
        :type path: str
        :return: Louw-Nida dictionary with the gloss and words for each sub-domain
        :rtype: dict
        """
        with open(path, mode='rb') as f:
            return pickle.load(f)


    def build_cats(self, ln):
        """ Finds Louw-Nida sub-domains that have at least 30 words in them and that do not belong to the more syntactic sub-domains

        :param ln: the Louw-Nida sub-domain dictionary
        :type ln: dict
        :return: the sub-domains that have at least 30 words in them and the first 30 words
        :rtype: dict
        """
        d = {}
        domains_to_remove = [89, 90, 91, 92, 93]
        for x in ln:
            if len(ln[x]['words']) > 29 and x[0] not in domains_to_remove:
                d[x] = [list(k.keys())[0] for k in ln[x]['words'][:30]]
        for k, v in d.items():
            d[k] = self.remove_doubles(v)
        return d


    def remove_doubles(self, seq):
        """ Convenience function to remove repeated words in any of the selected sub-domains

        :param seq: the sequence to be cleaned of repeated elements
        :type seq: iterable
        :return: the sequence without repeated elements
        :rtype: list
        """
        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x in seen or seen_add(x))]


    def clean_results(self, d):
        """ Goes through each of the chosen sub-domains and does two things:
             1) removes any words that occur in two domains with the same index - the meaning of these words is too ill-defined
             2) removes any words from a sub-domain where the index of that word is not the highest in any other sub-domain in which it occurs -
                this to try to get the sub-domain in which the word best belongs

        :param d: the sub-domain dictionary from build_cats()
        :type d: dict
        :return: cleaned dictionary of results
        :rtype: dict
        """
        doubles = []
        choices = {}
        for i1, x1 in d.items():
            for i2, x2 in enumerate(x1):
                if x2 in choices.keys():
                    if choices[x2]['index'] > i2:
                        choices[x2] = {'index': i2, 'list': i1}
                    elif choices[x2]['index'] == i2:
                        doubles.append(x2)
                else:
                    choices[x2] = {'index': i2, 'list': i1}
        for i, x in d.items():
            for y in doubles:
                if y in x:
                    d[i].remove(y)
        for i, x in d.items():
            for k in choices.keys():
                if k in x and choices[k]['list'] != i:
                    try:
                        d[i].remove(k)
                    except ValueError as E:
                        print(E, '{} already removed from list'.format(k))
        #for k, v in d.items():
            #d[k] = v[:10]
        return d

    def save_txt(self, d, folder):
        """ Saves the results to a tab-delimited text file with each sub-domains on one line

        :param d: the sub-domains with their words
        :type d: dict
        :param folder: the folder in which the .txt file should be saved
        :type folder: str
        """
        with open('{}/LN_test_domains2.txt'.format(folder), mode='w') as f:
            [f.write('{}\t{}\n'.format(k, '\t'.join(str(w) for w in v))) for k, v in sorted(d.items(), key=lambda x: int(x[0][:2]))]


class ByPrimary(BySize):

    def build_cats(self, ln):
        """ Returns only the Louw-Nida sub-domains that contain the primary meanings of at least 19 different words.
            These results will need to be cleaned by hand.

        :param ln: the Louw-Nida sub-domain dictionary
        :type ln: dict
        :return: the sub-domains that have at least 30 words in them and the first 30 words
        :rtype: dict
        """
        primary = {}
        domains_to_remove = [89, 90, 91, 92, 93]
        for k in ln.keys():
            if k[0] in domains_to_remove:
                continue
            for word in ln[k]['words']:
                if list(word.values())[0].startswith('a ') or ' ' not in list(word.values())[0][:2]:
                    try:
                        primary['{} {}'.format(k[0], ln[k]['gloss'])].append(list(word.items())[0][0])
                    except:
                        primary['{} {}'.format(k[0], ln[k]['gloss'])] = [list(word.items())[0][0]]
        new_primary = {}
        for k, v in primary.items():
            primary[k] = self.remove_doubles(v)
            if len(primary[k]) > 19:
                new_primary[k] = primary[k]
        return new_primary