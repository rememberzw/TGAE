#!python3
# -*- coding:utf8 -*-

import sys
import logging

from manage import Manage_Client

log = logging.getLogger('manage')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        cmd = 'help'
    else:
        cmd = sys.argv[1]

    Manage_Client.ManageClient().manage_client(cmd)
