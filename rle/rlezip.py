#!/usr/bin/env python

'''
Compresses a file using run-length encoding. A sentinel value of '*' is used.
TODO: To allow input files to contain the sentinel value, convert all instances
of '*' in the input to '**'.
'''

import getopt
import sys

# Constants
suffix = ".rlezip"
sentinel = '*'
bufsize = 4096
minrun = 4

def main():

    # Defaults
    infile = sys.stdin
    outfile = sys.stdout
    infilename = None
    outfilename = None
    doCompress = None

    # Parse flags
    try:
        opts, args = getopt.getopt(sys.argv[1:], "cdi:o:h")
    except getopt.GetoptError as err:
        print str(err) # Will print something like "option -a not recognized"
        usage()
    for o, a in opts:
        if o == "-c":
            doCompress = True
        elif o == "-d":
            doCompress = False
        elif o == "-i":
            infilename = a
        elif o == "-o":
            outfilename = a
        else:
            usage()

    # Get infilename from args if no flag was passed for it
    if len(sys.argv) >= 2 and infilename is None:
        infilename = sys.argv[1]

    # Decide whether we are compressing or decompressing based on the input file name
    if doCompress is None:
        if infilename.endswith(suffix):
            doCompress = False
        else:
            doCompress = True

    # Open files
    #
    # If given an input file, attempts to use an output file that either
    # appends or removes the compression file name suffix depending on whether
    # we are compressing or decompressing. Uses stdout if this is not possible.
    if infilename is not None:
        infile = open(infilename, 'r')
        if outfilename is None:
            if doCompress:
                outfilename = infilename+suffix
            else:
                if infilename.endswith(suffix) and len(infilename) > len(suffix):
                    outfilename = infilename[:-len(suffix)]
                else:
                    outfilename = None
    if outfilename is not None:
        outfile = open(outfilename, 'w')

    # Perform compression/decompression
    if doCompress:
        compress(infile, outfile)
    else:
        decompress(infile, outfile)

    # Close files
    if infilename is not None:
        infile.close()
        outfile.close()

def usage():
    print 'Usage: {0} [-h] [-c|-d] [-i ]infile [-o outfile]'.format(sys.argv[0])
    print '\t-h\tview this help'
    print '\t-c\tcompress the input file'
    print '\t-d\tdecompress the input file'
    print '\t-i\tinput file to compress, defaults to stdin'
    print '\t-o\toutput file to decompress, defaults to stdout or is based on infile.'
    sys.exit(2)

def compress(infile, outfile):
    while True:
        buf = infile.read(bufsize)
        if len(buf) == 0: break
        newbuf = ""
        lastchar = ''
        charcount = 0
        for char in buf:
            if char is lastchar:
                charcount += 1
            else:
                if charcount >= minrun and charcount <= 255:
                    newbuf += "{}{}{}".format(sentinel, lastchar, chr(charcount))
                    charcount = 1
                else:
                    newbuf += "{}".format(lastchar * charcount)
                    charcount = 1
            lastchar = char
        outfile.write(newbuf)
    outfile.write('\n')

def decompress(infile, outfile):
    while True:
        buf = infile.read(bufsize)
        if len(buf) == 0: break
        newbuf = ""
        state = 0
        for char in buf:
            # State 0: Normal
            # State 1: Have read a sentinel
            # State 2: Have read a sentinel and a char to repeat
            if state is 0 and char is sentinel:
                state = 1
            elif state is 1:
                repeatchar = char
                state = 2
            elif state is 2:
                newbuf += repeatchar * ord(char)
                state = 0
            else:
                newbuf += char
        outfile.write(newbuf)

if __name__ == '__main__':
    main()
