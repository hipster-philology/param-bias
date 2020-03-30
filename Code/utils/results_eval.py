from glob import glob

def eval_tsv(orig, dest, gensim_col):
    """ evaluates the results of a .tsv file produced by Code.Evaluate.Evaluator

    :param orig: directory containing the .tsv files
    :type orig: str
    :param dest: the destination file to save the results
    :type orig: str
    :param gensim_col: the column of the .tsv in which the Gensim outlier prediction is
    :type gensim_col: int
    """
    results = {}
    files = glob('{}/*.tsv'.format(orig))
    for file in files:
        results[file] = {'Gap Score': 0, 'Gensim': 0, 'Average': 0.0}
        total = 0
        with open(file) as f:
            lines = f.read().strip().split('\n')[1:]
        for line in lines:
            line = line.split('\t')
            total += float(line[0])
            if float(line[0]) > 0:
                results[file]['Gap Score'] += 1
            if line[gensim_col] == "1":
                results[file]['Gensim'] += 1
        results[file]['Average'] = total / len(lines)
    with open('results_analysis/{}.tsv'.format(dest), mode="w") as f:
        f.write('File\tGap Score Correct\tGensim Correct\tGap Score Average\n')
        for r, v in results.items():
            f.write('{}\t{}\t{}\t{}\n'.format(r, v['Gap Score'], v['Gensim'], v['Average']))
