"""The MIT License (MIT)

Copyright (c) 2015 Rob Renaud

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
# !/usr/bin/python
import math
import os
import pickle


class GibberishDetector:
    _accepted_chars = "abcdefghijklmnopqrstuvwxyz "
    _char_positions = dict([(char, idx) for idx, char in enumerate(_accepted_chars)])

    def __init__(self):
        with open(os.path.join(os.path.dirname(__file__), "gib_model.pki"), "rb") as f:
            self.model_data = pickle.load(f)

    def is_gibberish(self, item):
        model_mat = self.model_data["mat"]
        threshold = self.model_data["thresh"]
        return self._avg_transition_prob(item, model_mat) <= threshold

    def _avg_transition_prob(self, l, log_prob_mat):
        """ Return the average transition prob from l through log_prob_mat. """
        log_prob = 0.0
        transition_ct = 0
        for a, b in self._ngram(2, l):
            log_prob += log_prob_mat[self._char_positions[a]][self._char_positions[b]]
            transition_ct += 1
        # The exponentiation translates from log probs to probs.
        return math.exp(log_prob / (transition_ct or 1))

    def _ngram(self, n, l):
        """ Return all n grams from l after normalizing """
        filtered = self._normalize(l)
        for start in range(0, len(filtered) - n + 1):
            yield "".join(filtered[start : start + n])

    def _normalize(self, line):
        """ Return only the subset of chars from accepted_chars.
        This helps keep the  model relatively small by ignoring punctuation,
        infrequenty symbols, etc. """
        return [c.lower() for c in line if c.lower() in self._accepted_chars]
