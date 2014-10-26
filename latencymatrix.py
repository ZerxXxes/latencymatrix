#!/usr/bin/env python

import getpass
import os.path
import pxssh
import re
import subprocess
import sys
from argparse import ArgumentParser
from pymongo import MongoClient
from threading import Thread
from time import sleep, time

mongo = MongoClient().latencymatrix.tests

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

class Pinger(Thread):
    def __init__(self, from_host, to_host, username, password):
        super().__init__()

        self.from_host = from_host
        self.to_host = to_host
        self.username = username
        self.password = password

    def run(self):
        while True:
            try:
                self.conn = pxssh.pxssh()
                self.conn.login(self.from_host, self.username, self.password)

                while True:
                    self.do_test()
                    sleep(5)

            except pxssh.ExceptionPxssh as e:
                with print_lock:
                    print("pxssh failed on login, retrying in 10 seconds")
                    print(str(e))
                sleep(10)

    def do_test(self):
        self.conn.sendline("fping -C 3 -q -B1 -r1 -i10 %s" % self.to_host)   # do 5 icmp echo
        self.conn.readline() #hide the command sent to host
        self.conn.prompt()
        output = self.conn.before.decode("UTF-8")
        hostname, output = output.split(" : ")
        hostname = hostname.strip()

        pingtimes = []
        for pingtime in output.split(" "):
            if pingtime == "-":
                pingtimes.append(None)
            else:
                pingtimes.append(float(pingtime))

        print("%sRTT between %s <---> %s%s\n%s" %
              (bcolors.OKGREEN, self.from_host, self.to_host, bcolors.ENDC, pingtimes))

        self.conn.sendline ("traceroute -nAN 32 " + self.to_host) #traceroute to target and find AS_PATH
        self.conn.readline()
        self.conn.prompt()             # match the prompt
        output = self.conn.before.decode("UTF-8")

        asn_path = []
        for line in output.splitlines():
            matches = re.findall("\[AS(\d*)\]", line)
            if not matches:
                continue

            asn = int(matches[0])
            if not (1 <= asn <= 23455 or
                    23457 <= asn <= 64534 or
                    131072 <= asn <= 4199999999):
                continue # Not a public ASN

            if not asn_path or asn != asn_path[-1]:
                asn_path.append(asn)

        print("%sASN path between %s <---> %s%s\n%s" %
              (bcolors.OKGREEN, self.from_host, self.to_host, bcolors.ENDC, asn_path))

        mongo.insert({
            "timestamp": int(time()),
            "pingtimes": pingtimes,
            "asn_path": asn_path
        })

def main(argv):
    #check for arguments
    parser = ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("-p", "--ask-for-password", action="store_true")
    parser.add_argument("-i", "--install-ssh-keys", action="store_true")
    args = parser.parse_args()

    try:
        with open(args.file) as f:
            hostmatrix = [line.strip() for line in f]

    except IOError:
        print("There was an error reading", args.file)
        sys.exit()

    username = input('username: ')

    if args.install_ssh_keys:
        installsshkey(username, hostmatrix)
        return

    if args.ask_for_password:
        password = getpass.getpass('password: ')
    else:
        password = ""

    print('Input file is', args.file)
    print('Hosts found are:', hostmatrix)

    for from_host in hostmatrix:
        for to_host in hostmatrix:
            if from_host != to_host:
                Pinger(from_host, to_host, username, password).start()

    return hostmatrix;

def installsshkey(username, hostmatrix):
    #check if rsa-keys for this user already exists
    if os.path.exists(os.path.expanduser('~/.ssh/id_rsa.pub')):
        print("rsa-keys found, installing on hosts...")
    else:
        #if no rsa-key found, generate new ones
        print("no rsa-key found, generating...")
        subprocess.call('ssh-keygen -b 2048 -t rsa -f .ssh/id_rsa -q -N ""', shell=True)
        print("done")

    for currenthost in hostmatrix:
        subprocess.call("ssh-copy-id %s@%s" % (username, currenthost), shell=True)

if __name__ == "__main__":
    main(sys.argv[1:])
