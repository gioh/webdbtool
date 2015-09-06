from error import EchartsException
import re

class Base(object):
    
    def __init__(self):
        pass

    def convert_list(self, key=[]):
        result = "["
        for row in key:
            result += "'%s', " % row
        result = re.sub(",$", "", result)
        result += "]"
        return result

