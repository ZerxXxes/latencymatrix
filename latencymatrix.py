#!/usr/bin/env python

import sys, getopt

def main(argv):
  inputfile = ''
  try:
    opts, args = getopt.getopt(argv,"hi:",["ifile="])
  except getopt.GetoptError:
    print 'latencymatrix.py -i <inputfile> -o <outputfile>'
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print 'latencymatrix.py -i <inputfile>'
      sys.exit()
    elif opt in ("-i", "--ifile"):
      inputfile = arg
      #read list of hostnames to use in the matrix
      try:
        file = open(inputfile)
        hostmatrix = [line.strip() for line in open(inputfile)]
        file.close()
      except IOError:
        print "There was an error reading", inputfile
        sys.exit()
  print 'Input file is ', inputfile
  print 'hosts found are:\n', 
  for item in hostmatrix:
    print item
if __name__ == "__main__":
  main(sys.argv[1:])
