#!/usr/bin/env python

import sys, getopt, pxssh, getpass, thread

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def main(argv):
  #initate variables
  inputfile = ''
  interactive = 0
  #check for arguments
  try:
    opts, args = getopt.getopt(argv,"ihf:",["file="])
  #if no arguments show error and syntaxhelp
  except getopt.GetoptError:
    print 'latencymatrix.py -f <inputfile>'
    sys.exit(2)
  for opt, arg in opts:
    #show help
    if opt == '-h':
      print 'latencymatrix.py -f <inputfile>'
      sys.exit()
    if opt in ("-f", "--file"):
      inputfile = arg
      #read list of hostnames from inputfile to use in the matrix
      try:
        file = open(inputfile)
        hostmatrix = [line.strip() for line in open(inputfile)]
        file.close()
      except IOError:
        print "There was an error reading", inputfile
        sys.exit()
    if opt in ("-i", "--interactive"):
      interactive = 1
      print "Use interactive login"
  #Start DEBUG
  print 'Input file is ', inputfile
  print 'hosts found are:\n', 
  for item in hostmatrix:
    print item
  #Stop DEBUG
  if interactive:
      #hostname = raw_input('hostname: ')
      print "Enter login credentials for hosts"
      username = raw_input('username: ')
      password = getpass.getpass('password: ')
  else:
    print "derp"
  for currenthost in hostmatrix:
    remoteping(currenthost, hostmatrix, username, password)
  
  return hostmatrix;

def remoteping(currenthost, allhosts, username, password):
  try:
      s = pxssh.pxssh()
      s.login (currenthost, username, password)
      for target in allhosts:
        if target != currenthost:
          print bcolors.OKGREEN + "mesure RTT between", currenthost, "<--->", target + bcolors.ENDC
          s.sendline ("fping -qc 5 " + target)   # do 5 icmp echo
          s.prompt()
          print s.before
          s.sendline ("traceroute -nAN 32 " + target) #traceroute to target and find AS_PATH
          s.prompt()             # match the prompt
          print s.before          # print everything before the prompt.
      s.logout()
  except pxssh.ExceptionPxssh, e:
    print "pxssh failed on login."
    print str(e)
  return

if __name__ == "__main__":
  main(sys.argv[1:])