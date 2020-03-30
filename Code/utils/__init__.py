import pandas as pd

def pandas_most_sim(df, target, n_candidates=5):
    """ finds the most similar candidate words to a target word

    :param df: the dataframe containing the similarity scores
    :type df: pd.DataFrame
    :param target: the target word
    :type target: str
    :param n_candidates: the number of similaritiy candidates to return
    :type n_candidates: int
    :return: the n_candidate most similar words
    :rtype: list
    """
    return list(df.ix[target].sort_values(ascending=False).head(n_candidates + 1).index)[1:]
