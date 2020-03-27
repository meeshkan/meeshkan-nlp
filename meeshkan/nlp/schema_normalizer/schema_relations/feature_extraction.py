from typing import List
import re
import string
import spacy
import numpy as np


class FeatureExtraction:

    def __init__(self, multiple_vector=False, min_length=1):
        self.nlp = spacy.load('en_core_web_lg')
        self.multiple_vector = multiple_vector
        self.min_length = min_length

    def keep_only_alpha(self, tokens_list: List, keep_words=None, stop_words=None):
        if not isinstance(tokens_list, list):
            raise TypeError('The list of imput words is type list')

        list_of_words = []
        for word in tokens_list:
            word = re.sub(r'[^a-zA-Z]', ' ', word)
            word = word.split()
            list_of_words += word

        if self.min_length > 1:
            return [word for word in list_of_words if len(word) >= self.min_length]
        else:
            return list_of_words

    def is_camel_case(self, word):
        if any(x in word for x in string.punctuation) == True:
            return False
        else:
            if any(list(map(str.isupper, word[1:-1]))) == True:
                return True

            else:
                return False

    def camel_case_split_word(self, word):
        idx = list(map(str.isupper, word))
        # mark change of case
        l = [0]
        for (i, (x, y)) in enumerate(zip(idx, idx[1:])):
            if x and not y:  # "Ul"
                l.append(i)
            elif not x and y:  # "lU"
                l.append(i + 1)
        l.append(len(word))
        # for "lUl", index of "U" will pop twice, have to filer it
        return [word[x:y] for x, y in zip(l, l[1:]) if x < y]

    def camel_case_split_list(self, tokens_list):
        list_of_words = []
        for word in tokens_list:
            if self.is_camel_case(word):
                list_of_words += self.camel_case_split_word(word)
            else:
                list_of_words.append(word)

        return list_of_words

    def find_lemma_word(self, word):
        return self.nlp(word)[0].lemma_

    def find_lemma_list(self, tokens_list):
        return [self.find_lemma_word(word) for word in tokens_list]

    def remove_duplicate_and_sort(self, tokens_list):
        return sorted(list(set(tokens_list)))

    def convert_lower_word(self, word):
        return word.lower()

    def convert_lower_list(self, tokens_list):
        return [self.convert_lower_word(word) for word in tokens_list]

    def join_into_sentence(self, tokens_list, separator=' '):
        return separator.join(tokens_list)

    def sentence_vector(self, tokens_list: List):
        if self.multiple_vector:
            return np.array([self.nlp(word)[0].vector for word in tokens_list])
        else:
            sentence = self.join_into_sentence(tokens_list)
            return self.nlp(sentence).vector

    def generate_nlp_vector(self, tokens_list: List):
        tokens_list = self.keep_only_alpha(tokens_list)
        tokens_list = self.camel_case_split_list(tokens_list)
        tokens_list = self.convert_lower_list(tokens_list)
        tokens_list = self.find_lemma_list(tokens_list)
        tokens_list = self.remove_duplicate_and_sort(tokens_list)

        return self.sentence_vector(tokens_list)







# 