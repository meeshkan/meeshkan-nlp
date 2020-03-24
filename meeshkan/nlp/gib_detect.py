'''The MIT License (MIT)

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
'''
#!/usr/bin/python

import pickle
import meeshkan.nlp.gib_detect_train as gib_detect_train
#import gib_detect_train


class GibDetector:

    def __init__(self):

         self.model_data = pickle.load(open('../../../meeshkan/nlp/gib_model.pki', 'rb'))



    def gib_detector(self, item):

         l =item
         model_mat = self.model_data['mat']
         threshold = self.model_data['thresh']
         if not (gib_detect_train.avg_transition_prob(l, model_mat) > threshold):
             return True
         else:
            return False


'''              id.append(l)
              if len(id)!=0:
                   return id[-1]
              else:
                   return None
'''