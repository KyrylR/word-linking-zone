"""
Word Linkage Zone Library

This module provides the WordLinkageZone class for building a word-sentence linkage zone
from a corpus of texts. It processes the corpus and generates two text files:

1. A file containing, for each word in each sentence:
   - Text number
   - Sentence number
   - Word number in the sentence
   - Word form

2. A file containing:
   - Text number
   - Sentence number
   - Word number 1
   - Word number 2
   - Type of connection (dependency relation)

The library supports both English and Ukrainian languages and can be integrated into other codebases.

Example usage:

from word_linkage_zone import WordLinkageZone

wlz_uk = WordLinkageZone(language='uk')

# Sample corpus
corpus = [
    "Можна стверджувати, що проблема синтаксичного аналізу вирішується зараз індуктивним шляхом в рамках певних підмов.",
]

# Process the corpus
wlz_uk.process_corpus(corpus)

# Generate the output files
wlz_uk.generate_files(output_dir='output_en')
"""

import os
import spacy
from spacy.cli import download

import colorama
from colorama import Fore
from tabulate import tabulate

colorama.init(autoreset=True)

class WordLinkageZone:
    """
    A class for building a word-sentence linkage zone in a corpus.
    """

    def __init__(self, language='uk'):
        """
        Initialize the WordLinkageZone with a specified language.

        Args:
            language (str): The language code ('uk' for Ukrainian).
        """
        self.language = language
        self.nlp = self.load_language_model(language)
        self.word_data = []
        self.relation_data = []

    @staticmethod
    def load_language_model(language):
        """
        Load the spaCy language model for the specified language.

        Args:
            language (str): The language code.

        Returns:
            nlp: The spaCy language model.
        """
        model_name_map = {
            'uk': 'uk_core_news_lg'
        }

        if language not in model_name_map:
            raise ValueError(f"Unsupported language: {language}")

        model_name = model_name_map[language]

        try:
            nlp = spacy.load(model_name)
        except OSError:
            print(f"Downloading spaCy model for {language}: {model_name}")
            download(model_name)
            nlp = spacy.load(model_name)

        return nlp

    def process_corpus(self, corpus):
        """
        Process the corpus to build word-sentence linkage zones.

        Args:
            corpus (list): A list of texts (strings).
        """
        for text_index, text in enumerate(corpus):
            doc = self.nlp(text)
            for sent_index, sent in enumerate(doc.sents):
                word_list = []
                word_index_map = {}  # Map token indices to word numbers in the sentence
                for word_index, token in enumerate(sent):
                    word_number = word_index + 1  # Word number in the sentence, starting from 1
                    word_form = token.text
                    word_list.append({
                        'text_number': text_index + 1,
                        'sentence_number': sent_index + 1,
                        'word_number': word_number,
                        'word_form': word_form
                    })
                    word_index_map[token.i] = word_number  # Map global token index to local word number
                self.word_data.extend(word_list)

                # Process dependency relations
                for token in sent:
                    if token.head.i in word_index_map and token.dep_ != 'ROOT':
                        word_number1 = word_index_map[token.i]
                        word_number2 = word_index_map[token.head.i]
                        relation = token.dep_
                        self.relation_data.append({
                            'text_number': text_index + 1,
                            'sentence_number': sent_index + 1,
                            'word_number1': word_number1,
                            'word_number2': word_number2,
                            'relation': relation,
                            'dep_label': token.dep_
                        })

    def pretty_print(self):
        """
        Prints the word data and relation in an aligned format:
        word1 - relation (question) -> word2
        """
        table = []
        headers = [Fore.YELLOW + "Слово 1", Fore.YELLOW + "- Зв'язок (питання) ->", Fore.YELLOW + "Слово 2"]

        for rel in self.relation_data:
            word1 = self.get_word_form(rel['text_number'], rel['sentence_number'], rel['word_number2'])
            word2 = self.get_word_form(rel['text_number'], rel['sentence_number'], rel['word_number1'])
            relation_str = f"{spacy.glossary.explain(rel['dep_label'])}"

            colored_word1 = Fore.CYAN + word1
            colored_word2 = Fore.CYAN + word2
            colored_relation = Fore.MAGENTA + relation_str

            table.append([colored_word1, f"- {colored_relation} ->", colored_word2])

        # Print the table using tabulate for aligned columns
        print(tabulate(table, headers=headers, tablefmt="plain"))

    def get_word_form(self, text_number, sentence_number, word_number):
        """
        Get the word form for a given text, sentence, and word number.

        Args:
            text_number (int): The text number.
            sentence_number (int): The sentence number.
            word_number (int): The word number in the sentence.

        Returns:
            str: The word form.
        """
        for word in self.word_data:
            if (word['text_number'] == text_number and
                    word['sentence_number'] == sentence_number and
                    word['word_number'] == word_number):
                return word['word_form']
        return None

    def generate_files(self, output_dir):
        """
        Generate the two text files containing word and relation data.

        Args:
            output_dir (str): The directory to save the output files.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # First file: Word data
        file1_path = os.path.join(output_dir, 'words.txt')
        with open(file1_path, 'w', encoding='utf-8') as f:
            f.write('TextNumber\tSentenceNumber\tWordNumber\tWordForm\n')
            for word in self.word_data:
                f.write(f"{word['text_number']}\t{word['sentence_number']}\t"
                        f"{word['word_number']}\t{word['word_form']}\n")

        # Second file: Relation data
        file2_path = os.path.join(output_dir, 'relations.txt')
        with open(file2_path, 'w', encoding='utf-8') as f:
            f.write('TextNumber\tSentenceNumber\tWordNumber1\tWordNumber2\tRelation\n')
            for rel in self.relation_data:
                description = f"{spacy.glossary.explain(rel['dep_label'])}"
                f.write(f"{rel['text_number']}\t{rel['sentence_number']}\t"
                        f"{rel['word_number1']}\t{rel['word_number2']}\t{description}\n")
