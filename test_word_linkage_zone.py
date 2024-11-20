import unittest
import os
from word_linkage_zone import WordLinkageZone


class TestWordLinkageZone(unittest.TestCase):
    def setUp(self):
        self.ukrainian_corpus = [
            "Швидка бура лисиця стрибає через лінивого пса.",
            "Яблуко на день тримає лікаря далеко."
        ]
        self.output_dir = 'test_output'
        self.wlz = WordLinkageZone(language='uk')

    def tearDown(self):
        if os.path.exists(self.output_dir):
            for file_name in ['words.txt', 'relations.txt']:
                file_path = os.path.join(self.output_dir, file_name)

                if os.path.exists(file_path):
                    os.remove(file_path)

            os.rmdir(self.output_dir)

    def test_ukrainian_processing(self):
        self.wlz.process_corpus(self.ukrainian_corpus)
        self.wlz.generate_files(self.output_dir)
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'words.txt')))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'relations.txt')))

    def test_specific_ukrainian_sentence(self):
        self.wlz.process_corpus(["Можна стверджувати, що проблема синтаксичного аналізу вирішується зараз індуктивним шляхом в рамках певних підмов."])
        self.wlz.pretty_print()

