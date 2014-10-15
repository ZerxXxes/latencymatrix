#!/usr/bin/env python

import sys, getopt, pxssh, getpass, thread

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
    elif opt in ("-f", "--file"):
      inputfile = arg
      #read list of hostnames from inputfile to use in the matrix
      try:
        file = open(inputfile)
        hostmatrix = [line.strip() for line in open(inputfile)]
        file.close()
      except IOError:
        print "There was an error reading", inputfile
        sys.exit()
    elif opt in ("-i", "--interactive"):
      interactive = 1
      print "Use interactive login"
  #Start DEBUG
  print 'Input file is ', inputfile
  print 'hosts found are:\n', 
  for item in hostmatrix:
    print item
  #Stop DEBUG
  return hostmatrix;
def remoteping(currenthost, allhosts, username, password):
  try:
      s = pxssh.pxssh()
      s.login (currenthost, username, password)
      for target in allhosts:
        if target != currenthost:
          print "mesure RTT between", currenthost, "<--->", target
          s.sendline ("fping -qc 5 " + target)   # do 5 icmp echo
          s.prompt()             # match the prompt
          print s.before          # print everything before the prompt.
      s.logout()
  except pxssh.ExceptionPxssh, e:
    print "pxssh failed on login."
    print str(e)
  return

def setup(hostmatrix):
  #gather login credentials interactivly
  interactive = 1
  if interactive:
      #hostname = raw_input('hostname: ')
      print "Enter login credentials for hosts"
      username = raw_input('username: ')
      password = getpass.getpass('password: ')
  else:
    print "derp"
  for currenthost in hostmatrix:
    remoteping(currenthost, hostmatrix, username, password)
    # try:
    #   s = pxssh.pxssh()
    #   s.login (currenthost, username, password)
    #   for target in hostmatrix:
    #     if target != currenthost:
    #       print "mesure RTT between", currenthost, "<--->", target
    #       s.sendline ("fping -qc 5 " + target)   # do 5 icmp echo
    #       s.prompt()             # match the prompt
    #       print s.before          # print everything before the prompt.
    #   s.logout()

      #print "lol"
    # try:                                                            
    #   thread.start_new_thread( remoteping, (currenthost, hostmatrix, username, password) )
    # except:
    #   print "Error: unable to start thread"
  return;

if __name__ == "__main__":
  setup(main(sys.argv[1:]))