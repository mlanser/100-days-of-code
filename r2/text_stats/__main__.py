# text_stats/__main__.py

import sys
from .counter import count

segments = sys.argv[1:]
full_text = ' '.join(segments)

print('# words: {}, # chars: {}'.format(*count(full_text)))
