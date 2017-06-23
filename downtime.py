#!/usr/bin/env python2
# -*- coding: utf-8 -*-
'''
downtimes.py
'''

import os
import re
import sys
import socket, ssl
sys.dont_write_bytecode = True

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from ConfigParser import SafeConfigParser

class IRC(object):
    def __init__(self, network, port, nick):
        _socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        _socket.connect((network, port))
        self.regex = re.compile('NOTICE ' + nick)
        self.socket = ssl.wrap_socket(_socket)

    def send(self, string):
        self.socket.send(string.encode('utf-8'))

    def recv(self):
        string = ''
        x = 0
        while True:
            x += 1
            string += self.socket.recv(4096).decode('utf-8')
            match = self.regex.search(string)
            if match != None:
                break
        return string

def downtime(ns):
    data = ''
    msg = '{botname}: downtime {hostname} {duration} {reason}'.format(**ns.__dict__)
    if ns.verbose:
        print('msg =', msg)
    irc = IRC(ns.network, ns.port, ns.nick)
    irc.send('NICK %s\r\n' % ns.nick)
    irc.send('USER %s %s %s :My bot\r\n' % (ns.nick, ns.nick, ns.nick))
    response = irc.recv()
    if ns.verbose:
        print(response)
    irc.send('JOIN %s %s\r\n' % (ns.channel, ns.key))
    irc.send('PRIVMSG %s %s\r\n' % (ns.channel, msg))
    # FIXME: check for: downtime-bot: I'm sorry but I cannot find the host or service
    irc.send('QUIT\r\n')

def channel(string):
    if string.startswith('#'):
        return string
    return '#' + string

def load(config):
    defaults = {}
    parser = SafeConfigParser()
    if os.path.exists(config):
        parser.read([config])
        defaults = dict(parser.items('downtime'))
    return defaults

if __name__=='__main__':
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='turn on verbose printing')
    parser.add_argument(
        '-C', '--config',
        metavar='PATH',
        default='./downtime.cfg',
        help='default="%(default)s"; optional file to setup default values')
    ns, rem = parser.parse_known_args()
    defaults = load(ns.config)
    parser = ArgumentParser(
        parents=[parser],
        description=__doc__,
        formatter_class=RawDescriptionHelpFormatter)
    parser.set_defaults(**defaults)
    parser.add_argument(
        '-B', '--botname',
        help='default="%(default)s"; set the botname to be mentioned')
    parser.add_argument(
        '-N', '--network',
        help='default="%(default)s"; set the irc network')
    parser.add_argument(
        '-p', '--port',
        default=6697,
        type=int,
        help='default="%(default)s"; set the irc port')
    parser.add_argument(
        '-c', '--channel',
        type=channel,
        help='default="%(default)s"; set the channel')
    parser.add_argument(
        '-k', '--key',
        help='default="%(default)s"; set the key, if any')
    parser.add_argument(
        '-n', '--nick',
        default='downtime-bot',
        help='default="%(default)s"; set the nick to be used')
    parser.add_argument(
        '-d', '--duration',
        default='1h',
        help='default="%(default)s"; set the duration of the downtime')
    parser.add_argument(
        '-r', '--reason',
        default='patching',
        help='default="%(default)s"; set the reason of the downtime')
    parser.add_argument(
        'hostname',
        help='set the hostname that is being downtimed')

    ns = parser.parse_args()
    if ns.verbose:
        print(ns)
    downtime(ns)
