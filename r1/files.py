#!/usr/bin/env python3

import sys

def main(filename):
    f = open(filename, mode='rt', encoding='utf-8')
    
    print("\n-- [Printing cxonents from '{}'] --\n".format(filename))

    for line in f:
        sys.stdout.write(line)
    f.close()
    
    print("\n\n-- [The End] --\n")
    

if __name__ == '__main__':
    main(sys.argv[1])