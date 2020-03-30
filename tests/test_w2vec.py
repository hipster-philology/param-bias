from unittest import TestCase
from Code.WtoVec import W2VModel


class TestW2Vec(TestCase):
    def setUp(self):
        self.HalfCut = W2VModel("half-cut.no-pretrained", "data/transformed/half-cut")
        self.NoCut = W2VModel("no-cut.no-pretrained", "data/transformed/no-cut")

    def test_loading_file(self):
        self.assertEqual(len(self.HalfCut.texts), 172)
        self.assertEqual(len(self.NoCut.texts), 3)

    def test_sentences(self):
        self.assertIn(
            "Αδαμ Σηθ Ενως Καιναν Μαλελεηλ Ιαρεδ Ενωχ",
            sorted(self.HalfCut.sentences)[0]
        )