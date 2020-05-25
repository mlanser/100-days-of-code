# reader/multireader.py

import os

from reader.compressed import bzipped, gzipped

# This maps file extensions to corresponding open methods.
extension_map = {
    '.bz2': bzipped.opener,
    '.gz': gzipped.opener,
}


class MultiReader:
    def __init__(self, filename):
        extension = os.path.splitext(filename)[1]
        opener = extension_map.get(extension, open)
        self.f = opener(filename, mode='rt', encoding='utf-8')

    def close(self):
        self.f.close()
        
    def read(self):
        return self.f.read()