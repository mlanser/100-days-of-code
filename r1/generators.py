#!/usr/bin/env python3

"""Try out some generators.

Note:
    Some sample code from the book ... a bit enhanced tho :-)

Usage:
    python generators.py <func>
"""

import sys


def take(count, iterable):
    """Take items from the front of an iterable.
    Args:
        count:    The maximum number of items to retrieve.
        iterable: The source of the items.
    Yields:
        At most 'count' items from 'iterable'.
    """
    counter = 0
    for item in iterable:
        if counter == count:
            return
        counter += 1
        yield item


def run_take():
    items = [2, 4, 6, 8, 10]
    for item in take(3, items):
        print(item)



def distinct(iterable):
    """Return unique items by eliminating duplicates.
    Args:
        iterable: The source of the items.
    Yields:
        Unique elements in order from 'iterable'.
    """
    seen = set()
    for item in iterable:
        if item in seen:
            continue
        yield item
        seen.add(item)        
        
        
def run_distinct():
    items = [5, 7, 7, 6, 5, 5]
    for item in distinct(items):
        print(item)
        
        
def run_pipeline():
    items = [3, 6, 6, 2, 1, 1]
    for item in take(3, distinct(items)):
        print(item)


def lucas():
    yield 2
    a = 2
    b = 1
    
    while True:
        yield b
        a, b = b, a + b


def run_lucas(tot):
    if tot > 100:
        tot = 100
        
    for x in lucas():
        print(x)
        tot -= 1
        if tot <= 0:
            break


def main(fnc, tot = 0):
    """Main function of GENERATORS module.
    
    Args:
        fnc: name of function to run.
    """

    if fnc == 'take':
        run_take()
    elif fnc == 'distinct':
        run_distinct()
    elif fnc == 'pipeline':
        run_pipeline()
    elif fnc == 'lucas':
        run_lucas(int(tot))
    else:
        print("ERROR: Unknown function: '{}'\n".format(fnc))
        

if __name__ == '__main__':
    defaultFnc = 'pipeline'
    
    if len(sys.argv) >= 3:
        main(sys.argv[1], sys.argv[2])
    else:        
        try:
            main(sys.argv[1])
        except IndexError:
            print("\nWARNING: Missing FUNCTION NAME. Will use default function name '" + defaultFnc + "' for this operation.\n")
            main(defaultFnc)
