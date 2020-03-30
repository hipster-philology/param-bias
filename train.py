from Code.WtoVec import W2VModel
from Code.Evaluate import Evaluator
from argparse import ArgumentParser

EPOCHS = 1500
WORKERS = 7

simple_train = False  # When set to true, only train com-cut's + Greek
pretrained_only = False  # Only train pretrained


def run(
        simple_train=False,
        pretrained_only=False,
        EPOCHS=1500,
        WORKERS=7,
        testing_file="data/testing_groups.txt",
        evaluation_dir="results",
        is_training=False,
        nomatch=False
):
    """ Run training or evaluation

    :param simple_train: Train only the Complete Cut Corpora
    :param pretrained_only: Train only on the Greek pretrained
    :param EPOCHS: Number of epochs
    :param WORKERS: Number of workers
    :param testing_file: File to evaluate against
    :param evaluation_dir: Where to save evaluation
    :param is_training: Set training to run
    :return:
    """
    basic_kwargs = [
        ("1500e", dict(min_count=1, workers=WORKERS)),
        ("1500e.10w", dict(min_count=1, workers=WORKERS, window=10)),
        #("1500e.20w", dict(min_count=1, workers=WORKERS, window=20))
    ]
    #kwargs = [x for x in basic_kwargs]
    kwargs = [(name+".s200", {**kw, **{"size": 200}}) for name, kw in basic_kwargs]
    kwargs += [(name+".s50", {**kw, **{"size": 50}}) for name, kw in basic_kwargs]
    kwargs += [(name + ".s30", {**kw, **{"size": 30}}) for name, kw in basic_kwargs]
    kwargs += [(name + ".s80", {**kw, **{"size": 80}}) for name, kw in basic_kwargs]

    directories = [
        "data/transformed/com-cut/Full",
        "data/transformed/sup-cut/Full",
        "data/transformed/half-cut/Full",
        "data/transformed/no-cut/Full.txt"
    ]
    if simple_train is True:
        directories = [
            "data/transformed/com-cut/Full"
        ]

    for (name, params) in kwargs:
        print("Parameters : {}".format(", ".join(str(key)+":"+str(value) for key, value in params.items())))

        # GREEK
        Greek = W2VModel(
            "greek."+name,
            ["data/transformed/training-pandora-tb-grc", directories[0]],
            epochs=EPOCHS,
            parameters=params
        )
        if is_training:
            Greek.train()
        else:
            Greek.load()
        print("Base Greek Done")

        for directory in directories:

            print("Starting {}".format(directory))
            basename = directory.replace("/", ".")
            if pretrained_only is False:
                ComCut = W2VModel(
                    basename + name,
                    directory,
                    epochs=EPOCHS, parameters=params
                )
                if is_training:
                    ComCut.train()
                else:
                    ComCut.load()

                print("Without pretraining done")

                eval1 = Evaluator(ComCut, testing_file)
                eval1.score(evaluation_dir + "/" + basename + "." + name + ".tsv", nomatch=nomatch)
                print("Evaluation done")

            # Pretrained
            ComCut = W2VModel(
                basename + ".pretrained." + name,
                directory,
                epochs=EPOCHS, parameters=params, preload=Greek
            )
            if is_training:
                ComCut.train()
            else:
                ComCut.load()
            print("With pretraining done")

            eval1 = Evaluator(ComCut, testing_file)
            eval1.score(evaluation_dir + "/" + basename + ".pretrained." + name + ".tsv", nomatch=nomatch)
            print("Evaluation done")

            del ComCut
            del eval1

        del Greek

parser = ArgumentParser()
parser.add_argument("--simple", default=False, action="store_true", dest="simple_train", help="Only train on the complete cut corpora")
parser.add_argument("--pretrained", default=True, action="store_false", dest="pretrained_only", help="Only train the pretrained models")
parser.add_argument("--epochs", dest="EPOCHS", default=1500, help="Number of training epochs")
parser.add_argument("--workers", dest="WORKERS", default=7, help="Number of training workers")
parser.add_argument("--train", dest="is_training", default=False, action="store_true", help="Train the corpus")
parser.add_argument("--testing", dest="testing_file", default="data/testing_groups.txt", help="File to test against")
parser.add_argument("--evdir", dest="evaluation_dir", default="results", help="Directory for output")
parser.add_argument("--no-match", dest="nomatch", action="store_true", default=False, help="Compute match over four words using gensim")

if __name__ == "__main__":
    run(**vars(parser.parse_args()))
