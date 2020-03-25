from enum import Enum
from typing import Optional
import re

from dataclasses import dataclass
from meeshkan.nlp.entity_extractor import EntityExtractor
from  meeshkan.nlp.gib_detect import GibDetector
#from entity_extractor import EntityExtractor
#from gib_detect import GibDetector
from meeshkan.nlp.id_detector import IdClassifier


#id_type=Enum('int', 'hex', 'uuid', 'random')

@dataclass(frozen=True)
class IdDesc:
    value: Optional[str]
    type: Optional[IdType]


@dataclass(frozen=True)
class PathItems:
    entity: Optional[str]
    action: Optional[str]
    id: Optional[IdDesc]
    group_id: Optional[IdDesc]



class PathAnalyzer:
    def __init__(self):
        self._entity_extractor = EntityExtractor()
        self._gib_detector = GibDetector()
        self._id_classifier = IdClassifier()


    def extract_values(self, path):
        path_list=path.split('/')[1:] #/account/v1/accounts/dfd.3445f.4535 [account, v1, accounts, dfd.3445f.4535]
        nopunc_string=[]
        #  before this loop we have a list like ['border_account', 'jl865khh_hgyuf']

        #now we are trying to convert 'boeder_account' to ['border','account']
        # but we shouldnot touch id.
        #here we check for component in the list if it contain numbers then it is id and we should not touch it
        # if not => remove punctuation=> split to the parts

        for i in path_list:
            if len(re.findall('[0-9]+', i))!=0 :
                 nopunc_string.append(i)
            else:
                 i = re.sub('[^0-9a-z]+', ' ', i.lower())
                 for word in i.split(" "):
                     nopunc_string.append(word)
        pos= {value:index for index,value in enumerate(nopunc_string)}
        maybe_entity = self._entity_extractor._split_pathes(path_list)[-1]
        maybe_id = self._id_classifier.id_detector(path_list)
       # print(type(maybe_id))
        if maybe_id is not None:
            if pos[maybe_id]==pos[maybe_entity]+1:
                    return PathItems(entity=self._entity_extractor.get_entity_from_url(path_list), id=IdDesc(value=maybe_id, type=self._id_classifier.id_classif(maybe_id)) , action=None, group_id=None)
            else:
                    return PathItems(entity=self._entity_extractor.get_entity_from_url(path_list), id=None, id_type= None , action=None, group_id=None)
        else:
             return PathItems(entity=self._entity_extractor.get_entity_from_url(path_list), id=None, id_type= None , action=None, group_id=None)
 #       return PathItems(entity=self._entity_extractor.get_entity_from_url(path_list), id=id_classifier(path_list), action=None, group_id=None)
