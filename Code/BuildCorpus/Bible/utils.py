import re
from collections import defaultdict


def word_extract(text, pattern):
    """ Extracts a list of words from a list of strings in which these words are embedded.
        Only one word is extracted per list element

    :param text: list of strings that contain the words
    :type text: list
    :param pattern: regex pattern to use to extract the words from the strings in each line
    :type pattern: str
    :return: the words
    :rtype: list
    """
    words = []
    for line in text:
        words.append(re.sub(pattern, r'\1', line))
    return words


def word_cite_extract(text, pattern, split_int, corpus):
    """ Extracts the word and a citation string from each string in the list.
        Only one words and citation string are extracted per list element.

    :param text: list of strings that contain the words
    :type text: list
    :param pattern: regex pattern to use to extract the words from the strings in each line
    :type pattern: str
    :param split_int: integer representing how many elements to leave off of the split id string to get the citation string.
        E.g., if you want the first 3 elements in a 4 element string, the split_int should be 1
    :type split_int: int
    :return: the words split into the citation units
    :rtype: {str: list}
    """
    words = defaultdict(list)
    for line in text:
        c = re.sub('.+?id="([^"]*).*', r'\1', line).replace('/', '-')
        c = '/'.join(c.split('.')[:-split_int])
        c = corpus + '/' + c
        word = re.sub(pattern, r'\1', line)
        words[c].append(word)
    return words