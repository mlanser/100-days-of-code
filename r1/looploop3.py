#!/usr/bin/env python3

"""Retrieve and print words from a URL.

Note:
    This version uses (primitive) exception handling :-)

Usage:
    python looploop3.py <URL>
"""

import sys
from urllib.request import urlopen

def fetch_words(url):
    """Fetch a list of words from a URL.
    
    Args:
        url: The URL of a UTF-8 text document.
        
    Returns:
        Tuple with a list of strings containing the words from
        the document, total number of lines, and total number of chars.
    """
    
    story_words = []
    chars = 0
    lines = 0
    
    try:
        with urlopen(url) as story:

            for line in story:
                lines += 1
                line_words = line.decode('utf-8').split()

                for word in line_words:
                    chars += len(word)
                    story_words.append(word)
    except ValueError as e:
        print("\nERROR: {}\n".format(str(e)), file=sys.stderr)
        
    return story_words, lines, chars


def count_chars(words):
    """Count all chars in a list of words.
    
    Args:
        words: List of words.
        
    Returns:
        Returns total number of chars in list of words.
    """
    
    chars = 0
    
    for word in words:
        chars += len(word)
        
    return chars    


def print_stats(words, lines = None, chars = None):
    """Print basic stats for a list of words.
    
    Args:
        words: list of words.
        lines: number of lines.
        chars: number of chars in all words.
    """
    
    if chars == None:
        chars = count_chars(words)
    
    print('='.center(60, '='))
    print("Some core stats:\n")
    
    if lines != None:
        print("Num lines: {}".format(lines))
    
    print("Num words: {}".format(len(words)))
    print("Num chars: {}\n".format(chars))           

    
def print_words(words):
    """Print a list of words.
    
    Args:
        words: List of words.
    """
    
    print('='.center(60, '='))
    print("Print retrieved content, one word at a time:\n")
    for idx, word in enumerate(words):
        print('#{:4d}: {}'.format(idx + 1, word))
    print('='.center(60, '=') + "\n\n")

    
def main(url):
    """Main function of LOOPLOOP module.
    
    Args:
        url: The URL of a UTF-8 text document.
    """
    
    words, lines, chars = fetch_words(url)
    
    print_stats(words, lines, chars)
    print_words(words)
    

if __name__ == '__main__':
    defaultURL = 'http://sixty-north.com/c/t.txt'
    
    try:
        main(sys.argv[1])
    except IndexError:
        print("\nWARNING: Missing URL. Will use default URL '" + defaultURL + "' for this operation.\n")
        main(defaultURL)
