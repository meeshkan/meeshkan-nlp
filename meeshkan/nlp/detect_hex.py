import string

class HexDetector:

    def __init__(self):

         self.hex_digits = set(string.hexdigits)


    def hex_detector(self, item):
         if all(c in self.hex_digits for c in item):
             try:
                 int(item, 16)
                 return True

             except ValueError:
                 return False
         else:
             return False

'''hex=HexDetector()
while True:
    print('Insert a number:')
    i=input()
    print(hex.hex_detector(i))'''


