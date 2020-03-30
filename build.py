from Code.BuildCorpus.Bible.build import BuildBible
from Code.BuildCorpus.Greek import BuildGreek


#build = BuildBible()
greek = BuildGreek(["data/original/training-pandora-tb-grc/transition"], "data/transformed/training-pandora-tb-grc")
greek.run()
