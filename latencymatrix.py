#!/usr/bin/env python

import sys, getopt, pxssh, getpass, thread, os.path, subprocess

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
    opts, args = getopt.getopt(argv,"ihf:",["file=", "help"])
  #if no arguments show error and syntaxhelp
  except getopt.GetoptError:
    print "latencymatrix.py -f <inputfile>"
    sys.exit(2)
  for opt, arg in opts:
    #show help
    if opt in ("-h", "--help"):
      print "usage: latencymatrix [--interactive] [--automatic] [--help] [--file <inputfile>]"
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
          s.readline() #hide the command sent to host
          s.prompt()
          print s.before
          print bcolors.OKGREEN + "mesure path between", currenthost, "<--->", target + bcolors.ENDC
          s.sendline ("traceroute -nAN 32 " + target) #traceroute to target and find AS_PATH
          s.readline() 
          s.prompt()             # match the prompt
          print s.before          # print everything before the prompt.
      s.logout()
  except pxssh.ExceptionPxssh, e:
    print "pxssh failed on login."
    print str(e)
  return

def installsshkey(hostmatrix):
  #check if rsa-keys for this user already exists
  if os.path.exists(os.path.expanduser('~/.ssh/id_rsa.pub')):
    print "rsa-keys found, installing on hosts..."
  else:
  #if no rsa-key found, generate new ones
    print "no rsa-key found, generating..."
    subprocess.call("ssh-keygen" + ' -b 2048 -t rsa -f .ssh/id_rsa -q -N ""', shell=True)
    print "done"
  for currenthost in hostmatrix:
    #promt users about login to each server and then append user public key
    username = raw_input('username: ')
    password = getpass.getpass('password: ')
    s = pxssh.pxssh()
    s.login (currenthost, username, password)
    with open(os.path.expanduser('~/.ssh/id_rsa.pub'), 'r') as f:
      sendline ("echo " + f.readline() + " | cat >> .ssh/authorized_keys")
    f.closed
  pass

if __name__ == "__main__":
  main(sys.argv[1:])