#!/usr/bin/env python3

"""Retrieve and print words from a URL.

Usage:
    python looploop.py <URL>
"""

import sys
from urllib.request import urlopen

def fetch_words(url):
    """Fetch a list of words from a URL.
    
    Args:
        url: The URL of a UTF-8 text document.
        
    Returns:
        A list of strings containing the words from
        the document.
    """
    
    story_words = []

    with urlopen(url) as story:
    
        for line in story:
            line_words = line.decode('utf-8').split()
        
            for word in line_words:
                story_words.append(word)

    return story_words


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


def print_stats(words):
    """Print basic stats for a list of words.
    
    Args:
        words: List of words.
    """
    
    chars = count_chars(words)
    
    print('='.center(60, '='))
    print("Some core stats:\n")
    print("Num chars: " + str(chars))           
    print("Num words: " + str(len(words)) + "\n")

    
def print_words(words):
    """Print a list of words.
    
    Args:
        words: List of words.
    """
    
    print('='.center(60, '='))
    print("Print retrieved content, one word at a time:\n")
    for idx, word in enumerate(words):
        print('#{}: {}'.format(idx + 1, word))
    print('='.center(60, '=') + "\n\n")

    
def main(url):
    """Main function of LOOPLOOP module.
    
    Args:
        url: The URL of a UTF-8 text document.
    """
    
    if url == '':
        url = 'http://sixty-north.com/c/t.txt'
        
    words = fetch_words(url)
    
    print_stats(words)
    print_words(words)
    

if __name__ == '__main__':
    main(sys.argv[1])
